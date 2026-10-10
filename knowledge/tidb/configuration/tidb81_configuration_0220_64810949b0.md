# HTTP endpoint config.json and endpoint field definitions

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-app-config-files.md`
- Source Title: `Data App Configuration Files`
- Source Heading Path: `Data App Configuration Files > HTTP endpoint configuration | Data App Configuration Files > HTTP endpoint configuration > Endpoint configuration`
- Source Line Ranges: `87-192`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `http-endpoints`, `config-json`, `sql-file`, `parameters`, `path-parameters`, `pagination`, `cache`, `timeout`, `row-limit`, `batch-operation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0220_64810949b0`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-app-config-files.md#http-endpoint-configuration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d84aad39bc798c7c1b1872dbd79772e9004613167041d33d82796a944a35dd29`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files#http-endpoint-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-app-config-files.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the schema and field rules for `http_endpoints/config.json`, including endpoint methods, parameter definitions, path parameters, timeout, row limits, pagination, cache, batch mode, and SQL file mapping.
- Retrieval Keywords: HTTP endpoint configuration, http_endpoints/config.json, http_endpoints/sql/<method>-<endpoint-name>.sql, name, method, endpoint, data_source.cluster_id, params, params.name, params.type, params.required, params.default, params.enum, params.is_path_parameter, settings.timeout, settings.row_limit, settings.enable_pagination, settings.cache_enabled, settings.cache_ttl, batch_operation, sql_file, type, return_type, page, page_size, sql_endpoint, system-data, json
- Follow-up Guidance: The source states that mismatches between `params.is_path_parameter` and parameter placeholders in the `endpoint` field cause deployment failures.
- Classification Note: This is classified as configuration because the content specifies the JSON fields, allowed values, defaults, and constraints for Data App HTTP endpoint configuration.

## Official Source Content

## HTTP endpoint configuration

In your Data App directory, you can find endpoint configurations in `http_endpoints/config.json` and the SQL files in `http_endpoints/sql/<method>-<endpoint-name>.sql`.

```
├── <Your Data App directory>
│   ├── http_endpoints
│   │   ├── config.json
│   │   └── sql
│   │       ├── <method>-<endpoint-path1>.sql
│   │       ├── <method>-<endpoint-path2>.sql
│   │       └── <method>-<endpoint-path3>.sql
```
### Endpoint configuration

For each Data App, there can be one or multiple endpoints. You can find the configurations of all endpoints for a Data App in `http_endpoints/config.json`.

The following is an example configuration of `config.json`. In this example, there are two endpoints for this Data App.

```json
[
  {
    "name": "<Endpoint name1>",
    "description": "<Endpoint description1>",
    "method": "<HTTP method1>",
    "endpoint": "<Endpoint path1>",
    "data_source": {
      "cluster_id": <Cluster ID1>
    },
    "params": [],
    "settings": {
      "timeout": <Endpoint timeout>,
      "row_limit": <Maximum rows>,
      "enable_pagination": <0 | 1>,
      "cache_enabled": <0 | 1>,
      "cache_ttl": <time-to-live period>
    },
    "tag": "Default",
    "batch_operation": <0 | 1>,
    "sql_file": "<SQL file directory1>",
    "type": "sql_endpoint",
    "return_type": "json"
  },
  {
    "name": "<Endpoint name2>",
    "description": "<Endpoint description2>",
    "method": "<HTTP method2>",
    "endpoint": "<Endpoint path2>",
    "data_source": {
      "cluster_id": <Cluster ID2>
    },
    "params": [
      {
        "name": "<Parameter name>",
        "type": "<Parameter type>",
        "required": <0 | 1>,
        "default": "<Parameter default value>",
        "description": "<Parameter description>",
        "is_path_parameter": <true | false>
      }
    ],
    "settings": {
      "timeout": <Endpoint timeout>,
      "row_limit": <Maximum rows>,
      "enable_pagination": <0 | 1>,
      "cache_enabled": <0 | 1>,
      "cache_ttl": <time-to-live period>
    },
    "tag": "Default",
    "batch_operation": <0 | 1>,
    "sql_file": "<SQL file directory2>",
    "type": "sql_endpoint",
    "return_type": "json"
  }
]
```

The description of each field is as follows:

| Field         | Type   | Description |
|---------------|--------|-------------|
| `name`        | String | The endpoint name.            |
| `description` | String | (Optional) The endpoint description.          |
| `method`      | String | The HTTP method of the endpoint. You can use `GET` to retrieve data, use `POST` to create or insert data, use `PUT` to update or modify data, and use `DELETE` to delete data. |
| `endpoint`    | String | The unique path of the endpoint in the Data App. Only letters, numbers, underscores (`_`), and slashes (`/`) are allowed in the path, which must start with a slash (`/`) and end with a letter, number, or underscore (`_`). For example, `/my_endpoint/get_id`. The length of the path must be less than 64 characters.|
| `cluster_id`  | String | The ID of the TiDB cluster for your endpoint. You can get it from the URL of your TiDB cluster. For example, if your cluster URL is `https://tidbcloud.com/clusters/1234567891234567890/overview`, the cluster ID is `1234567891234567890`. |
| `params` | Array | The parameters used in the endpoint. By defining parameters, you can dynamically replace the parameter value in your queries through the endpoint. In `params`, you can define one or multiple parameters. For each parameter, you need to define its `name`, `type`, `required`, and `default` fields. If your endpoint does not need any parameters. You can leave `params` empty such as `"params": []`. |
| `params.name` | String | The name of the parameter. The name can only include letters, digits, and underscores (`_`) and must start with a letter or an underscore (`_`). **DO NOT** use `page` and `page_size` as parameter names, which are reserved for pagination of request results. |
| `params.type` | String | The data type of the parameter. Supported values are `string`, `number`, `integer`, `boolean`, and `array`. When using a `string` type parameter, you do not need to add quotation marks (`'` or `"`). For example, `foo` is valid for the `string` type and is processed as `"foo"`, whereas `"foo"` is processed as `"\"foo\""`. |
| `params.required` | Integer | Specifies whether the parameter is required in the request. Supported values are `0` (not required) and `1` (required). The default value is `0`.  |
| `params.enum` | String | (Optional) Specifies the value options of the parameter. This field is only valid when `params.type` is set to `string`, `number`, or `integer`. To specify multiple values, you can separate them with a comma (`,`). |
| `params.default` | String | The default value of the parameter. Make sure that the value matches the type of parameter you specified. Otherwise, the endpoint returns an error. The default value of an `ARRAY` type parameter is a string and you can use a comma (`,`) to separate multiple values. |
| `params.description` | String | The description of the parameter. |
| `params.is_path_parameter` | Boolean | Specifies whether the parameter is a path parameter. If it is set to `true`, ensure that the `endpoint` field contains the corresponding parameter placeholders; otherwise, it will cause deployment failures. Conversely, if the `endpoint` field contains the corresponding parameter placeholders but this field is set to `false`, it will also cause deployment failures. |
| `settings.timeout`     | Integer | The timeout for the endpoint in milliseconds, which is `30000` by default. You can set it to an integer from `1` to `60000`.  |
| `settings.row_limit`   | Integer  | The maximum number of rows that the endpoint can operate or return, which is `1000` by default. When `batch_operation` is set to `0`, you can set it to an integer from `1` to `2000`. When `batch_operation` is set to `1`, you can set it to an integer from `1` to `100`.  |
| `settings.enable_pagination`   | Integer  | Controls whether to enable the pagination for the results returned by the request. Supported values are `0` (disabled) and `1` (enabled). The default value is `0`. |
| `settings.cache_enabled`   | Integer  | Controls whether to cache the response returned by your `GET` requests within a specified time-to-live (TTL) period. Supported values are `0` (disabled) and `1` (enabled). The default value is `0`. |
| `settings.cache_ttl`   | Integer  | The time-to-live (TTL) period in seconds for cached response when `settings.cache_enabled` is set to `1`. You can set it to an integer from 30 to 600. During the TTL period, if you make the same `GET` requests again, Data Service returns the cached response directly instead of fetching data from the target database again, which improves your query performance. |
| `tag`    | String | The tag for the endpoint. The default value is `"Default"`. |
| `batch_operation`    | Integer | Controls whether to enable the endpoint to operate in batch mode. Supported values are `0` (disabled) and `1` (enabled). When it is set to `1`, you can operate on multiple rows in a single request. To enable this option, make sure that the request method is `POST` or `PUT`. |
| `sql_file`    | String | The SQL file directory for the endpoint. For example, `"sql/GET-v1.sql"`. |
| `type`        | String | The type of the endpoint. The value is `"system-data"` for predefined system endpoints and `"sql_endpoint"` for other endpoints. |
| `return_type` | String | The response format of the endpoint, which can only be `"json"`.             |
