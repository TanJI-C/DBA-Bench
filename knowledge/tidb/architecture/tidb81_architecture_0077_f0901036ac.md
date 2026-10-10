# Data Service concepts: data apps, endpoints, AI features, and configuration as code

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-concepts.md`
- Source Title: `Data Service (Beta)`
- Source Heading Path: `Data Service (Beta) | Data Service (Beta) > Data App | Data Service (Beta) > Data App endpoints | Data Service (Beta) > Chat2Query API | Data Service (Beta) > AI integrations | Data Service (Beta) > Configuration as Code`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `data service`, `data app`, `endpoints`, `api keys`, `https`, `serverless`, `sql execution`, `chat2query`, `ai integrations`, `github`, `configuration as code`, `auto sync`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0077_f0901036ac`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-concepts.md#data-service-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8829fa8b0cbf033c3977571a5e6eba59514b700c1e53f2dfa71bef5af13e584e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-concepts#data-service-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for the main concepts and capabilities of TiDB Cloud Data Service (Beta), including Data Apps, endpoints, Chat2Query API, AI integrations, and Configuration as Code with GitHub auto sync and deployment.
- Retrieval Keywords: Data Service (Beta), TiDB Cloud Data Service, Data App, Data App endpoints, API keys, HTTPS request, custom API endpoint, serverless architecture, execute SQL statements, WHERE clause, HTTP response, Chat2Query API, RESTful interface, generate and execute SQL statements using AI, AI integrations, GPTs, Dify, Configuration as Code, CaC, JSON syntax, GitHub, Auto Sync & Deployment, configuration files
- Follow-up Guidance: The source points to overview and task-specific pages for managing a Data App, managing an endpoint, using Chat2Query API, integrating third-party tools, and deploying a Data App automatically with GitHub.
- Classification Note: This chunk is classified as architecture because it defines the Data Service model and its core building blocks, interfaces, and configuration workflow in TiDB Cloud.

## Official Source Content

# Data Service (Beta)

TiDB Cloud [Data Service (beta)](https://tidbcloud.com/project/data-service) is a fully managed low-code backend-as-a-service solution that simplifies backend application development, empowering developers to rapidly build highly scalable, secure, data-driven applications.

Data Service enables you to access TiDB Cloud data via an HTTPS request using a custom API endpoint. This feature uses a serverless architecture to handle computing resources and elastic scaling, so you can focus on the query logic in endpoints without worrying about infrastructure or maintenance costs.

For more information, see [TiDB Cloud Data Service (Beta) Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview).
## Data App

A Data App in [Data Service (beta)](https://tidbcloud.com/project/data-service) is a collection of endpoints that you can use to access data for a specific application. By creating a Data App, you can group your endpoints and configure authorization settings using API keys to restrict access to endpoints. In this way, you can ensure that only authorized users can access and manipulate your data, making your application more secure.

For more information, see [Manage a Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app).
## Data App endpoints

An endpoint in [Data Service (beta)](https://tidbcloud.com/project/data-service) is a web API that you can customize to execute SQL statements. You can specify parameters for your SQL statements, such as the value used in the `WHERE` clause. When a client calls an endpoint and provides values for the parameters in a request URL, the endpoint executes the corresponding SQL statement with the provided parameters and returns the results as part of the HTTP response.

For more information, see [Manage an Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint).
## Chat2Query API

In TiDB Cloud, Chat2Query API is a RESTful interface that enables you to generate and execute SQL statements using AI by providing instructions. Then, the API returns the query results for you.

For more information, see [Get Started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api).
## AI integrations

Integrating third-party tools with your Data App enhances your applications with advanced natural language processing and artificial intelligence (AI) capabilities provided by third-party tools. This integration enables your applications to perform more complex tasks and deliver intelligent solutions.

Currently, you can integrate third-party tools, such as GPTs and Dify, in the TiDB Cloud console.

For more information, see [Integrate a Data App with Third-Party Tools](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-integrations).
## Configuration as Code

TiDB Cloud provides a Configuration as Code (CaC) approach to represent your entire Data App configurations as code using the JSON syntax.

By connecting your Data App to GitHub, TiDB Cloud can use the CaC approach and push your Data App configurations as [configuration files](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files) to your preferred GitHub repository and branch.

If Auto Sync & Deployment is enabled for your GitHub connection, you can also modify your Data App by updating its configuration files on GitHub. After you push the configuration file changes to GitHub, the new configurations will be deployed in TiDB Cloud automatically.

For more information, see [Deploy Data App Automatically with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection).
