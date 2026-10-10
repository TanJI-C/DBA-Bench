# OpenAPI enablement, API groups, and error format

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-open-api.md`
- Source Title: `Maintain DM Clusters Using OpenAPI`
- Source Heading Path: `Maintain DM Clusters Using OpenAPI | Maintain DM Clusters Using OpenAPI > APIs for managing clusters | Maintain DM Clusters Using OpenAPI > APIs for managing data sources | Maintain DM Clusters Using OpenAPI > APIs for managing replication tasks | Maintain DM Clusters Using OpenAPI > API error message template`
- Source Line Ranges: `5-91`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `openapi`, `enablement`, `topology`, `api-groups`, `error-format`, `swagger`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0220_ae5d8d7be5`
- Source ID: `tidb-docs-8.1:dm/dm-open-api.md#maintain-dm-clusters-using-openapi`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ef7f000ca13752720bb20d4ef94546f6511078467b374d1ed7eba6bf3d6db16`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-open-api#maintain-dm-clusters-using-openapi
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM OpenAPI enablement settings, the main API groups for cluster, data source, and replication task management, or the standard API error JSON format.
- Retrieval Keywords: openapi = true, server_configs master openapi: true, http://{master-addr}/api/v1/docs, OpenAPI 3.0.0, dm.yaml, Swagger Editor, GET /api/v1/docs, API error message template, error_msg, error_code, APIs for managing clusters, APIs for managing data sources, APIs for managing replication tasks
- Follow-up Guidance: The source also points to the OpenAPI specification document and the online docs endpoint at /api/v1/docs for request parameters and returned values.
- Classification Note: This is reference content because it defines how to enable DM OpenAPI, lists the available API groups, and shows the returned error message template.

## Official Source Content

# Maintain DM Clusters Using OpenAPI

DM provides the OpenAPI feature for easily querying and operating the DM cluster, which is similar to the feature of [dmctl tools](https://docs.pingcap.com/tidb/stable/dm/dmctl-introduction).

To enable OpenAPI, perform one of the following operations:

+ If your DM cluster has been deployed directly using binary, add the following configuration to the DM-master configuration file.

    ```toml
    openapi = true
    ```

+ If your DM cluster has been deployed using TiUP, add the following configuration to the topology file:

    ```yaml
    server_configs:
      master:
        openapi: true
    ```

> **Note:**
>
> - DM provides the [specification document](https://github.com/pingcap/tiflow/blob/release-8.1/dm/openapi/spec/dm.yaml) that meets the OpenAPI 3.0.0 standard. This document contains all the request parameters and returned values. You can copy the document yaml and preview it in [Swagger Editor](https://editor.swagger.io/).
>
> - After you deploy the DM-master nodes, you can access `http://{master-addr}/api/v1/docs` to preview the documentation online.
>
> - Some features supported in the configuration file are not supported in OpenAPI. Their capabilities are not fully aligned. In a production environment, it is recommended to use the [configuration file](https://docs.pingcap.com/tidb/stable/dm/dm-config-overview).

You can use the APIs to perform the following maintenance operations on the DM cluster:
## APIs for managing clusters

* [Get the information of a DM-master node](#get-the-information-of-a-dm-master-node)
* [Stop a DM-master node](#stop-a-dm-master-node)
* [Get the information of a DM-worker node](#get-the-information-of-a-dm-worker-node)
* [Stop a DM-worker node](#stop-a-dm-worker-node)
## APIs for managing data sources

* [Create a data source](#create-a-data-source)
* [Get a data source](#get-a-data-source)
* [Delete the data source](#delete-the-data-source)
* [Update a data source](#update-a-data-source)
* [Enable a data source](#enable-a-data-source)
* [Disable a data source](#disable-a-data-source)
* [Get the information of a data source](#get-the-information-of-a-data-source)
* [Get the data source list](#get-the-data-source-list)
* [Start the relay-log feature for data sources](#start-the-relay-log-feature-for-data-sources)
* [Stop the relay-log feature for data sources](#stop-the-relay-log-feature-for-data-sources)
* [Purge relay-log files that are no longer required](#purge-relay-log-files-that-are-no-longer-required)
* [Change the bindings between the data source and DM-workers](#change-the-bindings-between-the-data-source-and-dm-workers)
* [Get the list of schema names of a data source](#get-the-list-of-schema-names-of-a-data-source)
* [Get the list of table names of a specified schema in a data source](#get-the-list-of-table-names-of-a-specified-schema-in-a-data-source)
## APIs for managing replication tasks

* [Create a replication task](#create-a-replication-task)
* [Get a replication task](#get-a-replication-task)
* [Delete a replication task](#delete-a-replication-task)
* [Update a replication task](#update-a-replication-task)
* [Start a replication task](#start-a-replication-task)
* [Stop a replication task](#stop-a-replication-task)
* [Get the information of a replication task](#get-the-information-of-a-replication-task)
* [Get the replication task list](#get-the-replication-task-list)
* [Get the migration rules of a replication task](#get-the-migration-rules-of-a-replication-task)
* [Get the list of schema names of the data source that is associated with a replication task](#get-the-list-of-schema-names-of-the-data-source-that-is-associated-with-a-replication-task)
* [Get the list of table names of a specified schema in the data source that is associated with a replication task](#get-the-list-of-table-names-of-a-specified-schema-in-the-data-source-that-is-associated-with-a-replication-task)
* [Get the CREATE statement for schemas of the data source that is associated with a replication task](#get-the-create-statement-for-schemas-of-the-data-source-that-is-associated-with-a-replication-task)
* [Update the CREATE statement for schemas of the data source that is associated with a replication task](#update-the-create-statement-for-schemas-of-the-data-source-that-is-associated-with-a-replication-task)
* [Delete a schema of the data source that is associated with a replication task](#delete-a-schema-of-the-data-source-that-is-associated-with-a-replication-task)

The following sections describe the specific usage of the APIs.
## API error message template

After sending an API request, if an error occurs, the returned error message is in the following format:

```json
{
    "error_msg": "",
    "error_code": ""
}
```

From the above JSON output, `error_msg` describes the error message and `error_code` is the corresponding error code.
