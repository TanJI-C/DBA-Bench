# Data App directory, data source, and app config files

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-app-config-files.md`
- Source Title: `Data App Configuration Files`
- Source Heading Path: `Data App Configuration Files | Data App Configuration Files > Data source configuration | Data App Configuration Files > Data App configuration`
- Source Line Ranges: `5-86`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `data-app`, `github`, `directory-structure`, `data-source`, `cluster-id`, `app-config`, `app-id`, `app-version`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0219_cf854d5756`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-app-config-files.md#data-app-configuration-files`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `46ac57512ed96bafb4ec7c78e35a34b667af5ed074b56d642d739e7dfe3af6d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files#data-app-configuration-files
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-app-config-files.md

## Retrieval Guidance

- Use When: Use this chunk when locating the GitHub directory structure for a TiDB Cloud Data App and the definitions of `data_sources/cluster.json` and `dataapp_config.json` fields such as `cluster_id`, `app_id`, and `app_version`.
- Retrieval Keywords: Data App Configuration Files, data_sources/cluster.json, dataapp_config.json, cluster_id, app_id, app_name, app_type, app_version, description, Data App directory, GitHub directory structure, https://tidbcloud.com/clusters/1234567891234567890/overview
- Follow-up Guidance: It also shows the `http_endpoints` directory with `config.json` and `sql/<method>-<endpoint-path>.sql` files for endpoint configuration.
- Classification Note: This is classified as configuration because the content defines the Data App file layout and the JSON properties for data source and Data App configuration files.

## Official Source Content

# Data App Configuration Files

This document describes the configuration files of a [Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#data-app) in TiDB Cloud.

If you have [connected your Data App to GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection), you can find the configuration files of your Data App in your specified directory on GitHub as follows:

```
├── <Your Data App directory>
│   ├── data_sources
│   │   └── cluster.json
│   ├── dataapp_config.json
│   ├── http_endpoints
│   │   ├── config.json
│   │   └── sql
│   │       ├── <method>-<endpoint-path1>.sql
│   │       ├── <method>-<endpoint-path2>.sql
│   │       └── <method>-<endpoint-path3>.sql
```
## Data source configuration

The data source of a Data App comes from its linked TiDB clusters. You can find the data source configuration in `data_sources/cluster.json`.

```
├── <Your Data App directory>
│   ├── data_sources
│   │   └── cluster.json
```

For each Data App, you can link to one or multiple TiDB clusters.

The following is an example configuration of `cluster.json`. In this example, there are two linked clusters for this Data App.

```json
[
  {
    "cluster_id": <Cluster ID1>
  },
  {
    "cluster_id": <Cluster ID2>
  }
]
```

The field description is as follows:

| Field   | Type    | Description  |
|---------|---------|--------------|
| `cluster_id` | Integer | The ID of your TiDB cluster. You can get it from the URL of your cluster. For example, if your cluster URL is `https://tidbcloud.com/clusters/1234567891234567890/overview`, your cluster ID is `1234567891234567890`. |
## Data App configuration

The properties of a Data App contain the App ID, name, and type. You can find the properties in the `dataapp_config.json` file.

```
├── <Your Data App directory>
│   ├── dataapp_config.json
```

The following is an example configuration of `dataapp_config.json`.

```json
{
  "app_id": "<Data App ID>",
  "app_name": "<Data App name>",
  "app_type": "dataapi",
  "app_version": "<Data App version>",
  "description": "<Data App description>"
}
```

The description of each field is as follows:

| Field      | Type   | Description        |
|------------|--------|--------------------|
| `app_id`   | String | The Data App ID. Do not change this field unless your `dataapp_config.json` file is copied from another Data App and you want to update it to the ID of your current Data App. Otherwise, the deployment triggered by this modification will fail. |
| `app_name` | String | The Data App name. |
| `app_type` | String | The Data App type, which can only be `"dataapi"`. |
| `app_version` | String | The Data App version, which is in the `"<major>.<minor>.<patch>"` format. For example, `"1.0.0"`. |
| `description` | String | The Data App description. |
