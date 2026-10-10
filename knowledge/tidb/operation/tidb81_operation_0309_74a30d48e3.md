# Delete a Data App and related follow-up link

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-data-app.md`
- Source Title: `Manage a Data App`
- Source Heading Path: `Manage a Data App > Delete a Data App | Manage a Data App > Learn more`
- Source Line Ranges: `161-178`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `data app`, `deletion`, `endpoints`, `api keys`, `github connection`, `postman`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0309_74a30d48e3`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-data-app.md#delete-a-data-app`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63968c27b101a34379e7e0faf4be0bdae9a8bc8391a8505dc918020866286438`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#delete-a-data-app
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-data-app.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the prerequisites, UI steps, and effects of deleting a Data App in TiDB Cloud Data Service.
- Retrieval Keywords: Delete a Data App, Data Service, Danger Zone, Delete Data App, I understand, delete, <organization name>/<project name>/<data app name>, all endpoints are not online, Undeploy an endpoint, existing endpoints and API keys are also deleted, GitHub repository files are not deleted, Run Data App in Postman
- Follow-up Guidance: The page links to Undeploy an endpoint for making endpoints not online before deletion and to Run Data App in Postman in the Learn more section.
- Classification Note: This is classified as an operation because the content gives a step-by-step UI procedure to delete a Data App and notes the deletion prerequisites and outcomes.

## Official Source Content

## Delete a Data App

> **Note:**
>
> Before you delete a Data App, make sure that all endpoints are not online. Otherwise, you cannot delete the Data App. To undeploy an endpoint, refer to [Undeploy an endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#undeploy-an-endpoint).

To delete a Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, locate your target Data App and click the name of your target Data App to view its details.
3. In the **Danger Zone** area, click **Delete Data App**. A dialog box for confirmation is displayed.
4. Type your `<organization name>/<project name>/<data app name>`, and then click **I understand, delete**.

    Once a Data App is deleted, the existing endpoints and API keys in the Data App are also deleted. If this Data App is connected to GitHub, deleting the App does not delete the files in the corresponding GitHub repository.
## Learn more

- [Run Data App in Postman](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-postman-integration)
