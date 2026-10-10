# Relay log, source-worker binding, schema discovery, and task creation APIs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-open-api.md`
- Source Title: `Maintain DM Clusters Using OpenAPI`
- Source Heading Path: `Maintain DM Clusters Using OpenAPI > Start the relay-log feature for data sources | Maintain DM Clusters Using OpenAPI > Start the relay-log feature for data sources > Request URI | Maintain DM Clusters Using OpenAPI > Start the relay-log feature for data sources > Example | Maintain DM Clusters Using OpenAPI > Stop the relay-log feature for data sources | Maintain DM Clusters Using OpenAPI > Stop the relay-log feature for data sources > Request URI | Maintain DM Clusters Using OpenAPI > Stop the relay-log feature for data sources > Example | Maintain DM Clusters Using OpenAPI > Purge relay log files that are no longer required | Maintain DM Clusters Using OpenAPI > Purge relay log files that are no longer required > Request URI | Maintain DM Clusters Using OpenAPI > Purge relay log files that are no longer required > Example | Maintain DM Clusters Using OpenAPI > Change the bindings between the data source and DM-workers | Maintain DM Clusters Using OpenAPI > Change the bindings between the data source and DM-workers > Request URI | Maintain DM Clusters Using OpenAPI > Change the bindings between the data source and DM-workers > Example | Maintain DM Clusters Using OpenAPI > Get the list of schema names of a data source | Maintain DM Clusters Using OpenAPI > Get the list of schema names of a data source > Request URI | Maintain DM Clusters Using OpenAPI > Get the list of schema names of a data source > Example | Maintain DM Clusters Using OpenAPI > Get the list of table names of a specified schema in a data source | Maintain DM Clusters Using OpenAPI > Get the list of table names of a specified schema in a data source > Request URI | Maintain DM Clusters Using OpenAPI > Get the list of table names of a specified schema in a data source > Example | Maintain DM Clusters Using OpenAPI > Create a replication task | Maintain DM Clusters Using OpenAPI > Create a replication task > Request URI`
- Source Line Ranges: `572-723`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `openapi`, `relay-log`, `enable`, `disable`, `purge`, `worker-binding`, `schema`, `table`, `replication-task`, `request-uri`, `example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0222_3ab9c9fd23`
- Source ID: `tidb-docs-8.1:dm/dm-open-api.md#start-the-relay-log-feature-for-data-sources`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4d600261484420c203a10bd82c900c04e33cce689836be1f2692b9b2c80de485`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-open-api#start-the-relay-log-feature-for-data-sources
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM OpenAPI endpoints for relay log enable, disable, or purge operations, source-to-worker transfer, schema or table name discovery, or creating a replication task.
- Retrieval Keywords: POST /api/v1/sources/{source-name}/relay/enable, POST /api/v1/sources/{source-name}/relay/disable, POST /api/v1/sources/{source-name}/relay/purge, POST /api/v1/sources/{source-name}/transfer, GET /api/v1/sources/{source-name}/schemas, GET /api/v1/sources/{source-name}/schemas/{schema-name}, POST /api/v1/tasks, worker_name_list, relay_binlog_name, relay_binlog_gtid, relay_dir, worker_name, source-1/schemas, source-1/schemas/db1
- Follow-up Guidance: For the asynchronous relay and transfer APIs, the content says the latest status can be checked by getting the information of a data source or of a DM-worker node, while schema and table discovery return corresponding lists.
- Classification Note: This chunk is reference content because it lists DM OpenAPI request URIs, notes whether interfaces are synchronous or asynchronous, and provides example payloads for relay, binding, schema, table, and task APIs.

## Official Source Content

## Start the relay-log feature for data sources

This API is an asynchronous interface. If the request is successful, the status code of the returned body is 200. To learn about its latest status, You can [get the information of a data source](#get-the-information-of-a-data-source).
### Request URI

`POST /api/v1/sources/{source-name}/relay/enable`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01/relay/enable' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "worker_name_list": [
    "worker-1"
  ],
  "relay_binlog_name": "mysql-bin.000002",
  "relay_binlog_gtid": "e9a1fc22-ec08-11e9-b2ac-0242ac110003:1-7849",
  "relay_dir": "./relay_log"
}'
```
## Stop the relay-log feature for data sources

This API is an asynchronous interface. If the request is successful, the status code of the returned body is 200. To learn about its latest status, You can [get the information of a data source](#get-the-information-of-a-data-source).
### Request URI

`POST /api/v1/sources/{source-name}/relay/disable`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01/relay/disable' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "worker_name_list": [
    "worker-1"
  ]
}'
```
## Purge relay log files that are no longer required

This API is an asynchronous interface. If the request is successful, the status code of the returned body is 200. To learn about its latest status, You can [get the information of a data source](#get-the-information-of-a-data-source).
### Request URI

`POST /api/v1/sources/{source-name}/relay/purge`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01/relay/purge' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "relay_binlog_name": "mysql-bin.000002",
  "relay_dir": "string"
}'
```
## Change the bindings between the data source and DM-workers

This API is an asynchronous interface. If the request is successful, the status code of the returned body is 200. To learn about its latest status, You can [get the information of a DM-worker node](#get-the-information-of-a-dm-worker-node).
### Request URI

`POST /api/v1/sources/{source-name}/transfer`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/sources/mysql-01/transfer' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "worker_name": "worker-1"
}'
```
## Get the list of schema names of a data source

This API is a synchronous interface. If the request is successful, the corresponding list is returned.
### Request URI

`GET /api/v1/sources/{source-name}/schemas`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/sources/source-1/schemas' \
  -H 'accept: application/json'
```

```json
[
  "db1"
]
```
## Get the list of table names of a specified schema in a data source

This API is a synchronous interface. If the request is successful, the corresponding list is returned.
### Request URI

`GET /api/v1/sources/{source-name}/schemas/{schema-name}`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/sources/source-1/schemas/db1' \
  -H 'accept: application/json'
```

```json
[
  "table1"
]
```
## Create a replication task

This API is a synchronous interface. If the request is successful, the status code of the returned body is 200. A successful request will return the information of the corresponding replication task.
### Request URI

`POST /api/v1/tasks`
