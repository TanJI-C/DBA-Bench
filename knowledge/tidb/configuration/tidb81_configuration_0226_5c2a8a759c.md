# Develop an endpoint and configure properties

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-endpoint.md`
- Source Title: `Manage an Endpoint`
- Source Heading Path: `Manage an Endpoint > Develop an endpoint | Manage an Endpoint > Develop an endpoint > Configure properties`
- Source Line Ranges: `122-133`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `data-service`, `endpoint-development`, `properties`, `configuration`, `github`, `auto-sync`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0226_5c2a8a759c`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-endpoint.md#develop-an-endpoint`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c296eccb1791bccd7ee65f588d49213e355d7a49abe7e50a6bf3c244ce68efc9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#develop-an-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-endpoint.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what can be developed for a Data Service endpoint and where to configure endpoint properties, including the GitHub Auto Sync & Deployment note.
- Retrieval Keywords: Develop an endpoint, Configure properties, Properties tab, endpoint details page, write SQL statements, define parameters, manage the name and version, GitHub, Auto Sync & Deployment, Deploy automatically with GitHub
- Follow-up Guidance: The chunk states that if a Data App is connected to GitHub with Auto Sync & Deployment enabled, changes made in GitHub are deployed in TiDB Cloud Data Service automatically.
- Classification Note: This is classified as a configuration chunk because the content focuses on configurable endpoint elements such as SQL statements, parameters, name, version, and properties.

## Official Source Content

## Develop an endpoint

For each endpoint, you can write SQL statements to execute on a TiDB cluster, define parameters for the SQL statements, or manage the name and version.

> **Note:**
>
> If you have connected your Data App to GitHub with **Auto Sync & Deployment** enabled, you can also update the endpoint configurations using GitHub. Any changes you made in GitHub will be deployed in TiDB Cloud Data Service automatically. For more information, see [Deploy automatically with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection).
### Configure properties

On the right pane of the endpoint details page, you can click the **Properties** tab to view and configure properties of the endpoint.
