# Get, delete, and update replication task APIs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-open-api.md`
- Source Title: `Maintain DM Clusters Using OpenAPI`
- Source Heading Path: `Maintain DM Clusters Using OpenAPI > Get a replication task | Maintain DM Clusters Using OpenAPI > Get a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Get a replication task > Example | Maintain DM Clusters Using OpenAPI > Delete a replication task | Maintain DM Clusters Using OpenAPI > Delete a replication task > Request URI | Maintain DM Clusters Using OpenAPI > Delete a replication task > Example | Maintain DM Clusters Using OpenAPI > Update a replication task | Maintain DM Clusters Using OpenAPI > Update a replication task > Request URI`
- Source Line Ranges: `932-1078`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `openapi`, `replication-task`, `task-query`, `task-deletion`, `task-update`, `request-uri`, `example-response`, `synchronous-api`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0098_d8630e8afc`
- Source ID: `tidb-docs-8.1:dm/dm-open-api.md#get-a-replication-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c242be40d3b23715447351a2c84a333f362b4a1b33a9209b44b6147f28b55f15`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-open-api#get-a-replication-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the DM OpenAPI endpoints and examples to get, delete, or update a replication task.
- Retrieval Keywords: GET /api/v1/tasks/{task-name}?with_status=true, Delete a replication task, DELETE /api/v1/tasks/{task-name}, Update a replication task, PUT /api/v1/tasks/{task-name}, with_status=true, curl -X 'GET', curl -X 'DELETE', synchronous interface, Status Code 204, task-1
- Follow-up Guidance: The update section notes that when using this API to update task configuration, the task must be stopped, must have run into incremental sync, and only some fields can be updated.
- Classification Note: This is classified as operation because the content describes operational OpenAPI interfaces for querying, deleting, and updating an existing DM replication task.

## Official Source Content

## Get a replication task

This API is a synchronous interface. If the request is successful, the information of the corresponding replication task is returned.
### Request URI

`GET /api/v1/tasks/{task-name}?with_status=true`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1?with_status=true' \
  -H 'accept: application/json'
```

```json
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
```
## Delete a replication task

This interface is a synchronous interface and the Status Code of the returned body is 204 upon successful request.
### Request URI

`DELETE /api/v1/tasks/{task-name}`
### Example

```shell
curl -X 'DELETE' \
  'http://127.0.0.1:8261/api/v1/tasks/task-1' \
  -H 'accept: application/json'
```
## Update a replication task

This interface is a synchronous interface and a successful request returns the information of the task.

> **Note:**
>
> When you use this API to update the task configuration, make sure that the task is stopped and has run into incremental sync and that only some of the fields can be updated.
### Request URI

`PUT /api/v1/tasks/{task-name}`
