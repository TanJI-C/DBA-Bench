# Data source create, query, delete, and update APIs

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-open-api.md`
- Source Title: `Maintain DM Clusters Using OpenAPI`
- Source Heading Path: `Maintain DM Clusters Using OpenAPI > Create a data source | Maintain DM Clusters Using OpenAPI > Create a data source > Request URI | Maintain DM Clusters Using OpenAPI > Create a data source > Example | Maintain DM Clusters Using OpenAPI > Get a data source | Maintain DM Clusters Using OpenAPI > Get a data source > Request URI | Maintain DM Clusters Using OpenAPI > Get a data source > Example | Maintain DM Clusters Using OpenAPI > Delete the data source | Maintain DM Clusters Using OpenAPI > Delete the data source > Request URI | Maintain DM Clusters Using OpenAPI > Delete the data source > Example | Maintain DM Clusters Using OpenAPI > Update a data source | Maintain DM Clusters Using OpenAPI > Update a data source > Request URI`
- Source Line Ranges: `192-370`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `data-source`, `source-management`, `create-source`, `get-source`, `delete-source`, `update-source`, `relay-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0009_7e38e0a351`
- Source ID: `tidb-docs-8.1:dm/dm-open-api.md#create-a-data-source`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ead51980fca25d91e13af2f700a2d3ff3376852d6751b2c516f2153c41538b6e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-open-api#create-a-data-source
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the OpenAPI request URIs, example payloads, and response fields for creating, getting, deleting, or updating a DM data source.
- Retrieval Keywords: POST /api/v1/sources, GET /api/v1/sources/{source-name}, DELETE /api/v1/sources/{source-name}, PUT /api/v1/sources/{source-name}, with_status=true, force=true, source_name, enable_gtid, security.ssl_ca_content, cert_allowed_cn, purge.interval, status_list, relay_status, relay_config, relay_binlog_gtid, task_name_list, Create a data source, Get a data source, Delete the data source, Update a data source
- Follow-up Guidance: The source notes that when you use the update API to update the data source configuration, make sure that there are no running tasks under the current data source.
- Classification Note: This is data pipeline content because it covers lifecycle APIs for DM data sources, including configuration fields and relay status information tied to source management.

## Official Source Content

## Create a data source

This API is a synchronous interface. If the request is successful, the information of the corresponding data source is returned.
### Request URI

`POST /api/v1/sources`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/sources' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "source_name": "mysql-01",
  "host": "127.0.0.1",
  "port": 3306,
  "user": "root",
  "password": "123456",
  "enable": true,
  "enable_gtid": false,
  "security": {
    "ssl_ca_content": "",
    "ssl_cert_content": "",
    "ssl_key_content": "",
    "cert_allowed_cn": [
      "string"
    ]
  },
  "purge": {
    "interval": 3600,
    "expires": 0,
    "remain_space": 15
  }
}'
```

```json
{
  "source_name": "mysql-01",
  "host": "127.0.0.1",
  "port": 3306,
  "user": "root",
  "password": "123456",
  "enable": true,
  "enable_gtid": false,
  "security": {
    "ssl_ca_content": "",
    "ssl_cert_content": "",
    "ssl_key_content": "",
    "cert_allowed_cn": [
      "string"
    ]
  },
  "purge": {
    "interval": 3600,
    "expires": 0,
    "remain_space": 15
  },
  "status_list": [
    {
      "source_name": "mysql-replica-01",
      "worker_name": "worker-1",
      "relay_status": {
        "master_binlog": "(mysql-bin.000001, 1979)",
        "master_binlog_gtid": "e9a1fc22-ec08-11e9-b2ac-0242ac110003:1-7849",
        "relay_dir": "./sub_dir",
        "relay_binlog_gtid": "e9a1fc22-ec08-11e9-b2ac-0242ac110003:1-7849",
        "relay_catch_up_master": true,
        "stage": "Running"
      },
      "error_msg": "string"
    }
  ]
}
```
## Get a data source

This API is a synchronous interface. If the request is successful, the information of the corresponding data source is returned.
### Request URI

`GET /api/v1/sources/{source-name}`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/sources/source-1?with_status=true' \
  -H 'accept: application/json'
```

```json
{
  "source_name": "mysql-01",
  "host": "127.0.0.1",
  "port": 3306,
  "user": "root",
  "password": "123456",
  "enable_gtid": false,
  "enable": false,
  "flavor": "mysql",
  "task_name_list": [
    "task1"
  ],
  "security": {
    "ssl_ca_content": "",
    "ssl_cert_content": "",
    "ssl_key_content": "",
    "cert_allowed_cn": [
      "string"
    ]
  },
  "purge": {
    "interval": 3600,
    "expires": 0,
    "remain_space": 15
  },
  "status_list": [
    {
      "source_name": "mysql-replica-01",
      "worker_name": "worker-1",
      "relay_status": {
        "master_binlog": "(mysql-bin.000001, 1979)",
        "master_binlog_gtid": "e9a1fc22-ec08-11e9-b2ac-0242ac110003:1-7849",
        "relay_dir": "./sub_dir",
        "relay_binlog_gtid": "e9a1fc22-ec08-11e9-b2ac-0242ac110003:1-7849",
        "relay_catch_up_master": true,
        "stage": "Running"
      },
      "error_msg": "string"
    }
  ],
  "relay_config": {
    "enable_relay": true,
    "relay_binlog_name": "mysql-bin.000002",
    "relay_binlog_gtid": "e9a1fc22-ec08-11e9-b2ac-0242ac110003:1-7849",
    "relay_dir": "./relay_log"
  }
}
```
## Delete the data source

This API is a synchronous interface. If the request is successful, the status code of the returned body is 204.
### Request URI

`DELETE /api/v1/sources/{source-name}`
### Example

```shell
curl -X 'DELETE' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01?force=true' \
  -H 'accept: application/json'
```
## Update a data source

This API is a synchronous interface. If the request is successful, the information of the corresponding data source is returned.

> **Note:**
>
> When you use this API to update the data source configuration, make sure that there are no running tasks under the current data source.
### Request URI

`PUT /api/v1/sources/{source-name}`
