# Undeploy and delete a Data Service endpoint

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint > Undeploy an endpoint | Manage an Endpoint > Delete an endpoint`
- Source Line Ranges: `454-478`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `data-service`, `data-app`, `endpoint-lifecycle`, `undeploy`, `delete`, `github-sync`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0315_da10183b40`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#undeploy-an-endpoint`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1475f6ad61f5ba73246f355c7091a9a840d00d9b4355b2f4880f0918627a3d45`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#undeploy-an-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Data Service steps to undeploy or delete a Data App endpoint, including the condition that an endpoint must not be online before deletion.
- Retrieval Keywords: Undeploy an endpoint, Delete an endpoint, Data Service, Data App, endpoint, ... > Undeploy, ... > Delete, not online, cannot be deleted, Auto Sync & Deployment, GitHub, delete the configuration of this endpoint on GitHub
- Follow-up Guidance: If the Data App is connected to GitHub with Auto Sync & Deployment enabled, undeploying the endpoint also deletes that endpoint's configuration on GitHub.
- Classification Note: The content is classified as an operation because it provides procedural steps for endpoint lifecycle tasks in TiDB Cloud Data Service, specifically undeploying and deleting an endpoint.

## Official Source Content

## Undeploy an endpoint

> **Note:**
>
> If you have [connected your Data App to GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection) with **Auto Sync & Deployment** enabled, undeploying an endpoint of this Data App will also delete the configuration of this endpoint on GitHub.

To undeploy an endpoint, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its endpoints.
3. Locate the endpoint you want to undeploy, click **...** > **Undeploy**.
4. Click **Undeploy** to confirm the undeployment.
## Delete an endpoint

> **Note:**
>
> Before you delete an endpoint, make sure that the endpoint is not online. Otherwise, the endpoint cannot be deleted. To undeploy an endpoint, refer to [Undeploy an endpoint](#undeploy-an-endpoint).

To delete an endpoint, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its endpoints.
3. Click the name of the endpoint you want to delete, and then click **...** > **Delete** in the upper-right corner.
4. Click **Delete** to confirm the deletion.
