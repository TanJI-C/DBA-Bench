# TiCDC OpenAPI v2 overview, status and health APIs, and create changefeed request schema

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api-v2.md`
- Source Title: `TiCDC OpenAPI v2`
- Source Heading Path: `TiCDC OpenAPI v2 | TiCDC OpenAPI v2 > API error message template | TiCDC OpenAPI v2 > Return format of the API List interface | TiCDC OpenAPI v2 > Get the status information of a TiCDC node | TiCDC OpenAPI v2 > Get the status information of a TiCDC node > Request URI | TiCDC OpenAPI v2 > Get the status information of a TiCDC node > Example | TiCDC OpenAPI v2 > Check the health status of a TiCDC cluster | TiCDC OpenAPI v2 > Check the health status of a TiCDC cluster > Request URI | TiCDC OpenAPI v2 > Check the health status of a TiCDC cluster > Example | TiCDC OpenAPI v2 > Create a replication task | TiCDC OpenAPI v2 > Create a replication task > Request URI | TiCDC OpenAPI v2 > Create a replication task > Parameter descriptions`
- Source Line Ranges: `5-246`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `openapi`, `api-format`, `error-codes`, `list-response`, `node-status`, `cluster-health`, `changefeed`, `replication-task`, `request-uri`, `json-schema`, `sink-uri`, `replica-config`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0766_b97c26f40f`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api-v2.md#ticdc-openapi-v2`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a47e318ca37e46db41010a2a644d4a57ce2189fae1db5ac84062b945505f810`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#ticdc-openapi-v2
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api-v2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiCDC OpenAPI v2 reference details such as the common error JSON format, list response format, `GET /api/v2/status`, `GET /api/v2/health`, or the request schema for `POST /api/v2/changefeeds`.
- Retrieval Keywords: TiCDC OpenAPI v2, API error message template, error_msg, error_code, Return format of the API List interface, total, items, GET /api/v2/status, GET /api/v2/health, POST /api/v2/changefeeds, Create a replication task, changefeed_id, replica_config, sink_uri, start_ts, target_ts, liveness, is_owner, capture ID, 200 OK
- Follow-up Guidance: This chunk points to additional TiCDC OpenAPI v2 maintenance operations such as removing, updating, querying, pausing, and resuming replication tasks, querying subtasks and process lists, evicting an owner node, and dynamically adjusting the log level.
- Classification Note: This is reference content because it defines TiCDC OpenAPI v2 endpoints, JSON response conventions, and request parameter schema for node status, cluster health, and changefeed creation.

## Official Source Content

# TiCDC OpenAPI v2

TiCDC provides the OpenAPI feature for querying and operating the TiCDC cluster. The OpenAPI feature is a subset of the [`cdc cli` tool](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed).

> **Note:**
>
> TiCDC OpenAPI v1 will be removed in the future. It is recommended to use TiCDC OpenAPI v2.

You can use the APIs to perform the following maintenance operations on the TiCDC cluster:

- [Get the status information of a TiCDC node](#get-the-status-information-of-a-ticdc-node)
- [Check the health status of a TiCDC cluster](#check-the-health-status-of-a-ticdc-cluster)
- [Create a replication task](#create-a-replication-task)
- [Remove a replication task](#remove-a-replication-task)
- [Update the replication configuration](#update-the-replication-configuration)
- [Query the replication task list](#query-the-replication-task-list)
- [Query a specific replication task](#query-a-specific-replication-task)
- [Pause a replication task](#pause-a-replication-task)
- [Resume a replication task](#resume-a-replication-task)
- [Query the replication subtask list](#query-the-replication-subtask-list)
- [Query a specific replication subtask](#query-a-specific-replication-subtask)
- [Query the TiCDC service process list](#query-the-ticdc-service-process-list)
- [Evict an owner node](#evict-an-owner-node)
- [Dynamically adjust the log level of the TiCDC server](#dynamically-adjust-the-log-level-of-the-ticdc-server)

The request body and returned values of all APIs are in JSON format. A successful request returns a `200 OK` message. The following sections describe the specific usage of the APIs.

In the following examples, the listening IP address of the TiCDC server is `127.0.0.1` and the port is `8300`. You can specify the IP address and port bound to TiCDC via `--addr=ip:port` when starting the TiCDC server.
## API error message template

After an API request is sent, if an error occurs, the returned error message is in the following format:

```json
{
    "error_msg": "",
    "error_code": ""
}
```

In the above JSON output, `error_msg` describes the error message and `error_code` is the corresponding error code.
## Return format of the API List interface

If an API request returns a list of resources (for example, a list of all `Captures`), the TiCDC return format is as follows:

```json
{
  "total": 2,
  "items": [
    {
      "id": "d2912e63-3349-447c-90ba-wwww",
      "is_owner": true,
      "address": "127.0.0.1:8300"
    },
    {
      "id": "d2912e63-3349-447c-90ba-xxxx",
      "is_owner": false,
      "address": "127.0.0.1:8302"
    }
  ]
}
```

In the above example:

- `total`: indicates the total number of resources.
- `items`: an array that contains all the resources returned by this request. All elements of the array are of the same resource.
## Get the status information of a TiCDC node

This API is a synchronous interface. If the request is successful, the status information of the corresponding node is returned.
### Request URI

`GET /api/v2/status`
### Example

The following request gets the status information of the TiCDC node whose IP address is `127.0.0.1` and port number is `8300`.

```shell
curl -X GET http://127.0.0.1:8300/api/v2/status
```

```json
{
  "version": "v8.1.2",
  "git_hash": "10413bded1bdb2850aa6d7b94eb375102e9c44dc",
  "id": "d2912e63-3349-447c-90ba-72a4e04b5e9e",
  "pid": 1447,
  "is_owner": true,
  "liveness": 0
}
```

The parameters of the above output are described as follows:

- `version`: the current version number of TiCDC.
- `git_hash`: the Git hash value.
- `id`: the capture ID of the node.
- `pid`: the capture process ID (PID) of the node.
- `is_owner`: indicates whether the node is an owner.
- `liveness`: whether this node is live. `0` means normal. `1` means that the node is in the `graceful shutdown` state.
## Check the health status of a TiCDC cluster

This API is a synchronous interface. If the cluster is healthy, `200 OK` is returned.
### Request URI

`GET /api/v2/health`
### Example

```shell
curl -X GET http://127.0.0.1:8300/api/v2/health
```

If the cluster is healthy, the response is `200 OK` and an empty JSON object:

```json
{}
```

If the cluster is not healthy, the response is a JSON object containing the error message.
## Create a replication task

This interface is used to submit a replication task to TiCDC. If the request is successful, `200 OK` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v2/changefeeds`
### Parameter descriptions

```json
{
  "changefeed_id": "string",
  "replica_config": {
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
  "sink_uri": "string",
  "start_ts": 0,
  "target_ts": 0
}
```

The parameters are described as follows:

| Parameter name | Description |
| :------------------------ | :----------------------------------------------------- |
| `changefeed_id` | `STRING` type. The ID of the replication task. (Optional) |
| `replica_config` | Configuration parameters for the replication task. (Optional) |
| **`sink_uri`** | `STRING` type. The downstream address of the replication task. (**Required**) |
| `start_ts` | `UINT64` type. Specifies the start TSO of the changefeed. The TiCDC cluster will start pulling data from this TSO. The default value is the current time. (Optional) |
| `target_ts` | `UINT64` type. Specifies the target TSO of the changefeed. The TiCDC cluster stops pulling data when reaching this TSO. The default value is empty, meaning TiCDC does not stop automatically. (Optional) |

The meaning and format of `changefeed_id`, `start_ts`, `target_ts`, and `sink_uri` are the same as those described in the [Use `cdc cli` to create a replication task](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#create-a-replication-task) document. For the detailed description of these parameters, see that document. Note that when you specify the certificate path in `sink_uri`, make sure you have uploaded the corresponding certificate to the corresponding TiCDC server.

The descriptions of the `replica_config` parameters are as follows.
