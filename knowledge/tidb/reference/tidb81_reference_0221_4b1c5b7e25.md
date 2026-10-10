# Data source update, enable-disable, list, and status APIs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-open-api.md`
- Source Title: `Maintain DM Clusters Using OpenAPI`
- Source Heading Path: `Maintain DM Clusters Using OpenAPI > Update a data source > Example | Maintain DM Clusters Using OpenAPI > Enable a data source | Maintain DM Clusters Using OpenAPI > Enable a data source > Request URI | Maintain DM Clusters Using OpenAPI > Enable a data source > Example | Maintain DM Clusters Using OpenAPI > Disable a data source | Maintain DM Clusters Using OpenAPI > Disable a data source > Request URI | Maintain DM Clusters Using OpenAPI > Disable a data source > Example | Maintain DM Clusters Using OpenAPI > Get the data source list | Maintain DM Clusters Using OpenAPI > Get the data source list > Request URI | Maintain DM Clusters Using OpenAPI > Get the data source list > Example | Maintain DM Clusters Using OpenAPI > Get the information of a data source | Maintain DM Clusters Using OpenAPI > Get the information of a data source > Request URI | Maintain DM Clusters Using OpenAPI > Get the information of a data source > Example`
- Source Line Ranges: `371-571`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `openapi`, `data-source`, `update`, `enable`, `disable`, `list`, `status`, `request-uri`, `example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0221_4b1c5b7e25`
- Source ID: `tidb-docs-8.1:dm/dm-open-api.md#example`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a906443af7cb03707c1acb10d149f11633758f6477c4aa3fd5650373d72fe1e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-open-api#example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM OpenAPI endpoints and examples for updating a data source, enabling or disabling a source, listing sources, or getting a source status.
- Retrieval Keywords: PUT /api/v1/sources/{source-name}, POST /api/v1/sources/{source-name}/enable, POST /api/v1/sources/{source-name}/disable, GET /api/v1/sources, GET /api/v1/sources/{source-name}/status, with_status=true, source_name, enable_gtid, relay_status, worker_name, error_msg, curl http://127.0.0.1:8261/api/v1/sources/mysql-01/enable, curl http://127.0.0.1:8261/api/v1/sources/mysql-replica-01/status
- Follow-up Guidance: For a source status response, the content shows fields such as worker_name, relay_status, master_binlog, relay_binlog_gtid, relay_catch_up_master, stage, and error_msg.
- Classification Note: This chunk is reference content because it documents DM OpenAPI request URIs, synchronous behavior descriptions, and example request and response bodies for data source operations.

## Official Source Content

### Example

```shell
curl -X 'PUT' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "source": {
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
    "relay_config": {
      "enable_relay": true,
      "relay_binlog_name": "mysql-bin.000002",
      "relay_binlog_gtid": "e9a1fc22-ec08-11e9-b2ac-0242ac110003:1-7849",
      "relay_dir": "./relay_log"
    }
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
  }
}
```
## Enable a data source

This is a synchronous interface that enables a data source on a successful request and starts all subtasks of the task that rely on this data source in batch.
### Request URI

`POST /api/v1/sources/{source-name}/enable`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01/enable' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json'
```
## Disable a data source

This is a synchronous interface that deactivates this data source on a successful request and stops all subtasks of the task that rely on it in batch.
### Request URI

`POST /api/v1/sources/{source-name}/disable`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01/disable' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json'
```
## Get the data source list

This API is a synchronous interface. If the request is successful, the data source list is returned.
### Request URI

`GET /api/v1/sources`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/sources?with_status=true' \
  -H 'accept: application/json'
```

```json
{
  "data": [
    {
      "enable_gtid": false,
      "host": "127.0.0.1",
      "password": "******",
      "port": 3306,
      "purge": {
        "expires": 0,
        "interval": 3600,
        "remain_space": 15
      },
      "security": null,
      "source_name": "mysql-01",
      "user": "root"
    },
    {
      "enable_gtid": false,
      "host": "127.0.0.1",
      "password": "******",
      "port": 3307,
      "purge": {
        "expires": 0,
        "interval": 3600,
        "remain_space": 15
      },
      "security": null,
      "source_name": "mysql-02",
      "user": "root"
    }
  ],
  "total": 2
}
```
## Get the information of a data source

This API is a synchronous interface. If the request is successful, the information of the corresponding node is returned.
### Request URI

`GET /api/v1/sources/{source-name}/status`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-replica-01/status' \
  -H 'accept: application/json'
```

```json
{
  "total": 1,
  "data": [
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
