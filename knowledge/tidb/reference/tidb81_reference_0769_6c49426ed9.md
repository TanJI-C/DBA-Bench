# Create replication task response body schema

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api-v2.md`
- Source Title: `TiCDC OpenAPI v2`
- Source Heading Path: `TiCDC OpenAPI v2 > Create a replication task > Response body format`
- Source Line Ranges: `387-530`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `openapi`, `changefeed`, `response-body`, `schema`, `replication-task`, `task-status`, `error-fields`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0769_6c49426ed9`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api-v2.md#response-body-format`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `87c1d3ec6150ae9c9ab18a6a297fc8dbc0d005d9aa05c57e8ca7dee5cfdeb35a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#response-body-format
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api-v2.md

## Retrieval Guidance

- Use When: Use this when you need the TiCDC OpenAPI v2 response body schema returned for creating a replication task, including status fields, config structure, task_status, and error fields.
- Retrieval Keywords: Create a replication task response body format, TiCDC OpenAPI v2 changefeed response body schema, admin_job_type, checkpoint_time, checkpoint_ts, config, create_time, creator_version, error.addr, error.code, error.message, id, resolved_ts, sink_uri, start_ts, state normal stopped error failed finished, target_ts, task_status, capture_id, table_ids
- Follow-up Guidance: The source also states that the config structure and meaning are the same as the replica_config configuration used when creating the replication task.
- Classification Note: This is reference content because it defines the returned JSON fields and parameter meanings for the replication task response body.

## Official Source Content

### Response body format

```json
{
  "admin_job_type": 0,
  "checkpoint_time": "string",
  "checkpoint_ts": 0,
  "config": {
    "bdr_mode": true,
    "case_sensitive": false,
    "check_gc_safe_point": true,
    "consistent": {
      "flush_interval": 0,
      "level": "string",
      "max_log_size": 0,
      "storage": "string"
    },
    "enable_sync_point": true,
    "filter": {
      "event_filters": [
        {
          "ignore_delete_value_expr": "string",
          "ignore_event": [
            "string"
          ],
          "ignore_insert_value_expr": "string",
          "ignore_sql": [
            "string"
          ],
          "ignore_update_new_value_expr": "string",
          "ignore_update_old_value_expr": "string",
          "matcher": [
            "string"
          ]
        }
      ],
      "ignore_txn_start_ts": [
        0
      ],
      "rules": [
        "string"
      ]
    },
    "force_replicate": true,
    "ignore_ineligible_table": true,
    "memory_quota": 0,
    "mounter": {
      "worker_num": 0
    },
    "sink": {
      "column_selectors": [
        {
          "columns": [
            "string"
          ],
          "matcher": [
            "string"
          ]
        }
      ],
      "csv": {
        "delimiter": "string",
        "include_commit_ts": true,
        "null": "string",
        "quote": "string"
      },
      "date_separator": "string",
      "dispatchers": [
        {
          "matcher": [
            "string"
          ],
          "partition": "string",
          "topic": "string"
        }
      ],
      "enable_partition_separator": true,
      "encoder_concurrency": 0,
      "protocol": "string",
      "schema_registry": "string",
      "terminator": "string",
      "transaction_atomicity": "string"
    },
    "sync_point_interval": "string",
    "sync_point_retention": "string"
  },
  "create_time": "string",
  "creator_version": "string",
  "error": {
    "addr": "string",
    "code": "string",
    "message": "string"
  },
  "id": "string",
  "resolved_ts": 0,
  "sink_uri": "string",
  "start_ts": 0,
  "state": "string",
  "target_ts": 0,
  "task_status": [
    {
      "capture_id": "string",
      "table_ids": [
        0
      ]
    }
  ]
}
```

The parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `admin_job_type`  | `INTEGER` type. The admin job type.                 |
| `checkpoint_time` | `STRING` type. The formatted time of the current checkpoint for the replication task.                  |
| `checkpoint_ts`   | `STRING` type. The TSO of the current checkpoint for the replication task.    |
| `config`          | The replication task configuration. The structure and meaning are the same as that of the `replica_config` configuration in creating the replication task.       |
| `create_time`     | `STRING` type. The time when the replication task is created.                          |
| `creator_version` | `STRING` type. The TiCDC version when the replication task is created.         |
| `error`           | The replication task error.                      |
| `id`              | `STRING` type. The replication task ID.                |
| `resolved_ts`     | `UINT64` type. The replication task resolved ts.    |
| `sink_uri`        | `STRING` type. The replication task sink URI.                                     |
| `start_ts`        | `UINT64` type. The replication task start ts.                                      |
| `state`           | `STRING` type. The replication task status. It can be `normal`, `stopped`, `error`, `failed`, or `finished`. |
| `target_ts`       | `UINT64` type. The replication task target ts.                                    |
| `task_status`     | The detailed status of dispatching the replication task. |

The `task_status` parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `capture_id` | `STRING` type. The capture ID.                    |
| `table_ids`  | `UINT64 ARRAY` type. The ID of the table being replicated on this capture. |

The `error` parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `addr` | `STRING` type. The capture address. |
| `code` | `STRING` type. The error code.          |
| `message` | `STRING` type. The details of the error.      |
