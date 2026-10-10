# TiDB Cloud release notes: June to September 2024 updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2024.md`
- Source Title: `TiDB Cloud Release Notes in 2024`
- Source Heading Path: `TiDB Cloud Release Notes in 2024 > September 3, 2024 | TiDB Cloud Release Notes in 2024 > August 20, 2024 | TiDB Cloud Release Notes in 2024 > August 6, 2024 | TiDB Cloud Release Notes in 2024 > July 23, 2024 | TiDB Cloud Release Notes in 2024 > July 9, 2024 | TiDB Cloud Release Notes in 2024 > July 2, 2024 | TiDB Cloud Release Notes in 2024 > June 25, 2024`
- Source Line Ranges: `143-274`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`, `shared`
- Topic Tags: `release-notes`, `console-changes`, `serverless`, `dedicated`, `data-service`, `vector-search`, `billing`, `networking`, `import`, `export`, `private-endpoint`, `vpc-peering`, `system-status`, `slow-query`, `chat2query`, `sql-editor`, `budget`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0646_e1ffde6d08`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2024.md#september-3-2024`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a0e4a94b6e9f6e14eeffbd3c929f1e245d7a55328fe33d1723f492a743553e59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2024#september-3-2024
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2024.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud release-note details from June to September 2024 about console changes, Serverless and Dedicated updates, Data Service, vector search, billing, networking, import or export, System Status, slow query, Chat2Query or SQL Editor, and budget features.
- Retrieval Keywords: September 3 2024, August 20 2024, August 6 2024, July 23 2024, July 9 2024, July 2 2024, June 25 2024, TiDB Cloud Serverless export data in console, Export Data from TiDB Cloud Serverless, Configure External Storage Access for TiDB Cloud Serverless, TiDB Cloud Dedicated Connect dialog, cluster-level Networking page, Password Settings page, IP access list settings, Import page, AWS Role ARN, Create Private Endpoint Connection, Private Endpoint with AWS, Google Cloud Private Service Connect, billing details, TiDB Cloud Dedicated - Data Transfer - Load Balancing, public IPv4 addresses, v7.5.2, v7.5.3, Cluster Size, Create Cluster, Modify Cluster, Data Service beta, vector search endpoints, vector data types, Generate an endpoint automatically, Dify, GPTs, budget, Organization Owner, Organization Billing Admin, System Status, status.tidbcloud.com, VPC Peering, /system/query, sql parameter, slow query, vector search beta, vector index, vector functions and operators, LangChain, LlamaIndex, JinaAI, weekly email reports, Chat2Query API v3, /v1/chat2data, SQL Editor beta
- Follow-up Guidance: The content points to related docs such as Export Data from TiDB Cloud Serverless, Connect to TiDB Cloud Dedicated, Import data from files to TiDB Cloud, Manage budgets for TiDB Cloud, Add a predefined system endpoint, Vector search (beta) overview, and Get started with Chat2Query API.
- Classification Note: This is a TiDB Cloud release-notes chunk covering multiple dated updates across cloud console changes and general feature announcements for Serverless, Dedicated, Data Service, billing, and SQL-related capabilities.

## Official Source Content

## September 3, 2024

**Console changes**

- Support exporting data from TiDB Cloud Serverless clusters using the [TiDB Cloud console](https://tidbcloud.com/). 
  
    Previously, TiDB Cloud only supported exporting data using the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference). Now, you can easily export data from TiDB Cloud Serverless clusters to local files and Amazon S3 in the [TiDB Cloud console](https://tidbcloud.com/). 
  
    For more information, see [Export Data from TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export) and [Configure External Storage Access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage).

- Enhance the connection experience for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    - Revise the **Connect** dialog interface to provide TiDB Cloud Dedicated users with a more streamlined and efficient connection experience.
    - Introduce a new cluster-level **Networking** page to simplify network configuration for your cluster.
    - Replace the **Security Settings** page with a new **Password Settings** page and move IP access list settings to the new **Networking** page.
  
  For more information, see [Connect to TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster).

- Enhance the data import experience for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters:

    - Refine the layout of the **Import** page with a clearer layout.
    - Unify the import steps for TiDB Cloud Serverless and TiDB Cloud Dedicated clusters.
    - Simplify the AWS Role ARN creation process for easier connection setup.

  For more information, see [Import data from files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-migration-overview#import-data-from-files-to-tidb-cloud).
## August 20, 2024

**Console changes**

- Refine the layout of the **Create Private Endpoint Connection** page to improve the user experience for creating new private endpoint connections in [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    For more information, see [Connect to a TiDB Cloud Dedicated Cluster via Private Endpoint with AWS](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections) and [Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud).
## August 6, 2024

**General changes**

- [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) billing changes for load balancing on AWS.

    Starting from August 1, 2024, TiDB Cloud Dedicated bills include new AWS charges for public IPv4 addresses, aligned with [AWS pricing changes effective from February 1, 2024](https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights/). The charge for each public IPv4 address is $0.005 per hour, which will result in approximately $10 per month for each TiDB Cloud Dedicated cluster hosted on AWS.

    This charge will appear under the existing **TiDB Cloud Dedicated - Data Transfer - Load Balancing** service in your [billing details](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#billing-details).

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v7.5.2](https://docs.pingcap.com/tidb/v7.5/release-7.5.2) to [v7.5.3](https://docs.pingcap.com/tidb/v7.5/release-7.5.3).

**Console changes**

- Enhance the cluster size configuration experience for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).

    Refine the layout of the **Cluster Size** section on the [**Create Cluster**](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster) and [**Modify Cluster**](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster) pages for TiDB Cloud Dedicated clusters. In addition, the **Cluster Size** section now includes links to node size recommendation documents, which helps you select an appropriate cluster size.
## July 23, 2024

**General changes**

- [Data Service (beta)](https://tidbcloud.com/project/data-service) supports automatically generating vector search endpoints.

    If your table contains [vector data types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types), you can automatically generate a vector search endpoint that calculates vector distances based on your selected distance function.

    This feature enables seamless integration with AI platforms such as [Dify](https://docs.dify.ai/guides/tools) and [GPTs](https://openai.com/blog/introducing-gpts), enhancing your applications with advanced natural language processing and AI capabilities for more complex tasks and intelligent solutions.

    For more information, see [Generate an endpoint automatically](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#generate-an-endpoint-automatically) and [Integrate a Data App with Third-Party Tools](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-integrations).

- Introduce the budget feature to help you track actual TiDB Cloud costs against planned expenses, preventing unexpected costs.

    To access this feature, you must be in the `Organization Owner` or `Organization Billing Admin` role of your organization.

    For more information, see [Manage budgets for TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-budget).
## July 9, 2024

**General changes**

- Enhance the [System Status](https://status.tidbcloud.com/) page to provide better insights into TiDB Cloud system health and performance.

    To access it, visit <https://status.tidbcloud.com/> directly, or navigate via the [TiDB Cloud console](https://tidbcloud.com) by clicking **?** in the lower-right corner and selecting **System Status**.

**Console changes**

- Refine the **VPC Peering** page layout to improve the user experience for [creating VPC Peering connections](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) in [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.
## July 2, 2024

**General changes**

- [Data Service (beta)](https://tidbcloud.com/project/data-service) provides an endpoint library with predefined system endpoints that you can directly add to your Data App, reducing the effort in your endpoint development.

    Currently, the library only includes the `/system/query` endpoint, which enables you to execute any SQL statement by simply passing the statement in the predefined `sql` parameter. This endpoint facilitates the immediate execution of SQL queries, enhancing flexibility and efficiency.

    For more information, see [Add a predefined system endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#add-a-predefined-system-endpoint).

- Enhance slow query data storage.

    The slow query access on the [TiDB Cloud console](https://tidbcloud.com) is now more stable and does not affect database performance.
## June 25, 2024

**General changes**

- [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) supports vector search (beta).

    The vector search (beta) feature provides an advanced search solution for performing semantic similarity searches across various data types, including documents, images, audio, and video. This feature enables developers to easily build scalable applications with generative artificial intelligence (AI) capabilities using familiar MySQL skills. Key features include:

    - [Vector data types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types), [vector index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index), and [vector functions and operators](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-functions-and-operators).
    - Ecosystem integrations with [LangChain](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain), [LlamaIndex](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-llamaindex), and [JinaAI](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-jinaai-embedding).
    - Programming language support for Python: [SQLAlchemy](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-sqlalchemy), [Peewee](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-peewee), and [Django ORM](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-django-orm).
    - Sample applications and tutorials: perform semantic searches for documents using [Python](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-get-started-using-python) or [SQL](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-get-started-using-sql).

  For more information, see [Vector search (beta) overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview).

- [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) now offers weekly email reports for organization owners.

    These reports provide insights into the performance and activity of your clusters. By receiving automatic weekly updates, you can stay informed about your clusters and make data-driven decisions to optimize your clusters.

- Release Chat2Query API v3 endpoints and deprecate the Chat2Query API v1 endpoint `/v1/chat2data`.

    With Chat2Query API v3 endpoints, you can start multi-round Chat2Query by using sessions.

    For more information, see [Get started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api).

**Console changes**

- Rename Chat2Query (beta) to SQL Editor (beta).

    The interface previously known as Chat2Query is renamed to SQL Editor. This change clarifies the distinction between manual SQL editing and AI-assisted query generation, enhancing usability and your overall experience.

    - **SQL Editor**: the default interface for manually writing and executing SQL queries in the TiDB Cloud console.
    - **Chat2Query**: the AI-assisted text-to-query feature, which enables you to interact with your databases using natural language to generate, rewrite, and optimize SQL queries.

  For more information, see [Explore your data with AI-assisted SQL Editor](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query).
