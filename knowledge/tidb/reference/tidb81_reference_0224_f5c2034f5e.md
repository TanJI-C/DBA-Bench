# Replication task lifecycle and inspection APIs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-open-api.md`
- Source Title: `Maintain DM Clusters Using OpenAPI`
- Source Heading Path: `Maintain DM Clusters Using OpenAPI > Start a replication task | Maintain DM Clusters Using OpenAPI > Start a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Start a replication task > Example | Maintain DM Clusters Using OpenAPI > Stop a replication task | Maintain DM Clusters Using OpenAPI > Stop a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Stop a replication task > Example | Maintain DM Clusters Using OpenAPI > Get the information of a replication task | Maintain DM Clusters Using OpenAPI > Get the information of a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Get the information of a replication task > Example | Maintain DM Clusters Using OpenAPI > Get the replication task list | Maintain DM Clusters Using OpenAPI > Get the replication task list > Request URI | Maintain DM Clusters Using OpenAPI > Get the replication task list > Example | Maintain DM Clusters Using OpenAPI > Get the migration rules of a replication task | Maintain DM Clusters Using OpenAPI > Get the migration rules of a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Get the migration rules of a replication task > Example | Maintain DM Clusters Using OpenAPI > Get the list of schema names of the data source that is associated with a replication task | Maintain DM Clusters Using OpenAPI > Get the list of schema names of the data source that is associated with a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Get the list of schema names of the data source that is associated with a replication task > Example | Maintain DM Clusters Using OpenAPI > Get the list of table names of a specified schema in the data source that is associated with a replication task | Maintain DM Clusters Using OpenAPI > Get the list of table names of a specified schema in the data source that is associated with a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Get the list of table names of a specified schema in the data source that is associated with a replication task > Example`
- Source Line Ranges: `1287-1595`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `openapi`, `replication-task`, `start`, `stop`, `status`, `task-list`, `migration-rules`, `schemas`, `tables`, `asynchronous-api`, `synchronous-api`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0224_f5c2034f5e`
- Source ID: `tidb-docs-8.1:dm/dm-open-api.md#start-a-replication-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f53175c4be103e25596ac9a777593f87a9221e304fc1d75a144660a89a4857ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-open-api#start-a-replication-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need DM OpenAPI endpoints and examples for starting, stopping, checking status, listing tasks, viewing migrate targets, or listing schemas and tables associated with a replication task.
- Retrieval Keywords: Start a replication task, POST /api/v1/tasks/{task-name}/start, Stop a replication task, POST /api/v1/tasks/{task-name}/stop, Get the information of a replication task, GET /api/v1/tasks/task-1/status, stage=running, Get the replication task list, GET /api/v1/tasks, Get the migration rules of a replication task, GET /api/v1/tasks/{task-name}/sources/{source-name}/migrate_targets, source_schema, source_table, target_schema, target_table, Get the list of schema names of the data source that is associated with a replication task, GET /api/v1/tasks/{task-name}/sources/{source-name}/schemas, Get the list of table names of a specified schema in the data source that is associated with a replication task, GET /api/v1/tasks/{task-name}/sources/{source-name}/schemas/{schema-name}, asynchronous interface, synchronous interface, status code 204, status code 200, load_status, sync_status, worker_name, unit, unresolved_ddl_lock_id, finished_bytes, total_bytes, meta_binlog, meta_binlog_gtid, total_events, total_tps, recent_tps, master_binlog, master_binlog_gtid, syncer_binlog, syncer_binlog_gtid, blocking_ddls, unresolved_groups, seconds_behind_master
- Follow-up Guidance: For the latest status after a successful start or stop request, the source says you can get the information of a replication task.
- Classification Note: This is reference content because it enumerates replication task lifecycle and inspection APIs, their request URIs, interface type, and example responses.

## Official Source Content

## Start a replication task

This API is an asynchronous interface. If the request is successful, the status code of the returned body is 204. To learn the latest status of a task, You can [get the information of a replication task](#get-the-information-of-a-replication-task).
### Request URI

`POST /api/v1/tasks/{task-name}/start`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1/start' \
  -H 'accept: */*'
```
## Stop a replication task

This API is an asynchronous interface. If the request is successful, the status code of the returned body is 200. To learn the latest status of a task, You can [get the information of a replication task](#get-the-information-of-a-replication-task).
### Request URI

`POST /api/v1/tasks/{task-name}/stop`
### Example

```shell
curl -X 'POST' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1/stop' \
  -H 'accept: */*'
```
## Get the information of a replication task

This API is a synchronous interface. If the request is successful, the information of the corresponding node is returned.
### Request URI

`GET /api/v1/tasks/task-1/status`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1/status?stage=running' \
  -H 'accept: application/json'
```

```json
{
  "total": 1,
  "data": [
    {
      "name": "string",
      "source_name": "string",
      "worker_name": "string",
      "stage": "running",
      "unit": "sync",
      "unresolved_ddl_lock_id": "string",
      "load_status": {
        "finished_bytes": 0,
        "total_bytes": 0,
        "progress": "string",
        "meta_binlog": "string",
        "meta_binlog_gtid": "string"
      },
      "sync_status": {
        "total_events": 0,
        "total_tps": 0,
        "recent_tps": 0,
        "master_binlog": "string",
        "master_binlog_gtid": "string",
        "syncer_binlog": "string",
        "syncer_binlog_gtid": "string",
        "blocking_ddls": [
          "string"
        ],
        "unresolved_groups": [
          {
            "target": "string",
            "ddl_list": [
              "string"
            ],
            "first_location": "string",
            "synced": [
              "string"
            ],
            "unsynced": [
              "string"
            ]
          }
        ],
        "synced": true,
        "binlog_type": "string",
        "seconds_behind_master": 0
      }
    }
  ]
}
```
## Get the replication task list

This API is a synchronous interface and a successful request returns a list of the corresponding tasks.
### Request URI

`GET /api/v1/tasks`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/tasks' \
  -H 'accept: application/json'
```

```json
{
  "total": 2,
  "data": [
    {
      "name": "task-1",
      "task_mode": "all",
      "shard_mode": "pessimistic",
      "meta_schema": "dm-meta",
      "enhance_online_schema_change": true,
      "on_duplicate": "overwrite",
      "target_config": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "security": {
          "ssl_ca_content": "",
          "ssl_cert_content": "",
          "ssl_key_content": "",
          "cert_allowed_cn": [
            "string"
          ]
        }
      },
      "binlog_filter_rule": {
        "rule-1": {
          "ignore_event": [
            "all dml"
          ],
          "ignore_sql": [
            "^Drop"
          ]
        },
        "rule-2": {
          "ignore_event": [
            "all dml"
          ],
          "ignore_sql": [
            "^Drop"
          ]
        },
        "rule-3": {
          "ignore_event": [
            "all dml"
          ],
          "ignore_sql": [
            "^Drop"
          ]
        }
      },
      "table_migrate_rule": [
        {
          "source": {
            "source_name": "source-name",
            "schema": "db-*",
            "table": "tb-*"
          },
          "target": {
            "schema": "db1",
            "table": "tb1"
          },
          "binlog_filter_rule": [
            "rule-1",
            "rule-2",
            "rule-3",
          ]
        }
      ],
      "source_config": {
        "full_migrate_conf": {
          "export_threads": 4,
          "import_threads": 16,
          "data_dir": "./exported_data",
          "consistency": "auto",
          "import_mode": "physical",
          "sorting_dir": "./sort_dir",
          "disk_quota": "80G",
          "checksum": "required",
          "analyze": "optional",
          "range_concurrency": 0,
          "compress-kv-pairs": "",
          "pd_addr": "",
          "on_duplicate_logical": "error",
          "on_duplicate_physical": "none"
        },
        "incr_migrate_conf": {
          "repl_threads": 16,
          "repl_batch": 100
        },
        "source_conf": [
          {
            "source_name": "mysql-replica-01",
            "binlog_name": "binlog.000001",
            "binlog_pos": 4,
            "binlog_gtid": "03fc0263-28c7-11e7-a653-6c0b84d59f30:1-7041423,05474d3c-28c7-11e7-8352-203db246dd3d:1-170"
          }
        ]
      }
    }
  ]
}
```
## Get the migration rules of a replication task

This API is a synchronous interface and a successful request returns a list of the migration rules of this task.
### Request URI

`GET /api/v1/tasks/{task-name}/sources/{source-name}/migrate_targets`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1/sources/source-1/migrate_targets' \
  -H 'accept: application/json'
```

```json
{
  "total": 0,
  "data": [
    {
      "source_schema": "db1",
      "source_table": "tb1",
      "target_schema": "db1",
      "target_table": "tb1"
    }
  ]
}
```
## Get the list of schema names of the data source that is associated with a replication task

This API is a synchronous interface. If the request is successful, the corresponding list is returned.
### Request URI

`GET /api/v1/tasks/{task-name}/sources/{source-name}/schemas`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1/sources/source-1/schemas' \
  -H 'accept: application/json'
```

```json
[
  "db1"
]
```
## Get the list of table names of a specified schema in the data source that is associated with a replication task

This API is a synchronous interface. If the request is successful, the corresponding list is returned.
### Request URI

`GET /api/v1/tasks/{task-name}/sources/{source-name}/schemas/{schema-name}`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1/sources/source-1/schemas/db1' \
  -H 'accept: application/json'
```

```json
[
  "table1"
]
```
