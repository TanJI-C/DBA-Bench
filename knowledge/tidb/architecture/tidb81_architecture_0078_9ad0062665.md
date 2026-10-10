# Data Service overview, scenarios, and next steps

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-overview.md`
- Source Title: `TiDB Cloud Data Service (Beta) Overview`
- Source Heading Path: `TiDB Cloud Data Service (Beta) Overview | TiDB Cloud Data Service (Beta) Overview > Scenarios | TiDB Cloud Data Service (Beta) Overview > What's next`
- Source Line Ranges: `5-40`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `data-service`, `endpoints`, `https`, `serverless`, `data-apps`, `api-keys`, `chat2query`, `scenarios`, `web-api`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0078_9ad0062665`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-overview.md#tidb-cloud-data-service-beta-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d8a7b71f6eaa777c7415210dc4d953fdeb03765034f9767fadffe8feb96126ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview#tidb-cloud-data-service-beta-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for what TiDB Cloud Data Service (Beta) is, how endpoints and Data Apps work, common HTTPS access scenarios, or what to read next.
- Retrieval Keywords: TiDB Cloud Data Service (Beta) Overview, Data Service, endpoint, Data App, API keys, HTTPS request, custom API endpoint, serverless architecture, TiDB Cloud Serverless, Dedicated clusters contact TiDB Cloud Support, Chat2Query API, Chat2Data endpoint, web API execute SQL statements, parameters in WHERE clause, mobile or web application, serverless edge functions, database connection pooling, data visualization projects, MySQL interface does not support, Get Started with Data Service, Manage a Data App, Manage an Endpoint
- Follow-up Guidance: The source points to Get Started with Data Service, Get Started with Chat2Query API, Manage a Data App, and Manage an Endpoint for next steps.
- Classification Note: This is classified as architecture because the content is an overview of the TiDB Cloud Data Service model, including endpoints, Data Apps, HTTPS access, serverless architecture, and usage scenarios.

## Official Source Content

# TiDB Cloud Data Service (Beta) Overview

TiDB Cloud [Data Service (beta)](https://tidbcloud.com/project/data-service) is a fully managed low-code backend-as-a-service solution that simplifies backend application development, empowering developers to rapidly build highly scalable, secure, data-driven applications.

Data Service enables you to access TiDB Cloud data via an HTTPS request using a custom API endpoint. This feature uses a serverless architecture to handle computing resources and elastic scaling, so you can focus on the query logic in endpoints without worrying about infrastructure or maintenance costs.

> **Note:**
>
> Data Service is available for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters. To use Data Service in TiDB Cloud Dedicated clusters, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

An endpoint in Data Service is a web API that you can customize to execute SQL statements. You can specify parameters for your SQL statements, such as the value used in the `WHERE` clause. When a client calls an endpoint and provides values for the parameters in a request URL, the endpoint executes the corresponding SQL statement with the provided parameters and returns the results as part of the HTTP response.

To manage endpoints more efficiently, you can use Data Apps. A Data App in Data Service is a collection of endpoints that you can use to access data for a specific application. By creating a Data App, you can group your endpoints and configure authorization settings using API keys to restrict access to endpoints. In this way, you can ensure that only authorized users can access and manipulate your data, making your application more secure.

> **Tip:**
>
> TiDB Cloud provides a Chat2Query API for TiDB clusters. After it is enabled, TiDB Cloud will automatically create a system Data App called **Chat2Query** and a Chat2Data endpoint in Data Service. You can call this endpoint to let AI generate and execute SQL statements by providing instructions.
>
> For more information, see [Get started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api).
## Scenarios

Data Service allows you to seamlessly integrate TiDB Cloud with any application or service that is compatible with HTTPS. The following are some typical usage scenarios:

- Access the database of your TiDB cluster directly from a mobile or web application.
- Use serverless edge functions to call endpoints and avoid scalability issues caused by database connection pooling.
- Integrate TiDB Cloud with data visualization projects by using Data Service as a data source. This avoids exposing your database connection username and password, making your API more secure and easier to use.
- Connect to your database from an environment that the MySQL interface does not support. This provides more flexibility and options for you to access data.
## What's next

- [Get Started with Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-get-started)
- [Get Started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api)
- [Manage a Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app)
- [Manage an Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint)
