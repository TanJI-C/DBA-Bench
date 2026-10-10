# Changefeed and processor query, pause, and resume APIs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api.md`
- Source Title: `TiCDC OpenAPI v1`
- Source Heading Path: `TiCDC OpenAPI v1 > Query the replication task list > Parameter description > Query parameters | TiCDC OpenAPI v1 > Query the replication task list > Example | TiCDC OpenAPI v1 > Query a specific replication task | TiCDC OpenAPI v1 > Query a specific replication task > Request URI | TiCDC OpenAPI v1 > Query a specific replication task > Parameter description | TiCDC OpenAPI v1 > Query a specific replication task > Parameter description > Path parameters | TiCDC OpenAPI v1 > Query a specific replication task > Example | TiCDC OpenAPI v1 > Pause a replication task | TiCDC OpenAPI v1 > Pause a replication task > Request URI | TiCDC OpenAPI v1 > Pause a replication task > Parameter description | TiCDC OpenAPI v1 > Pause a replication task > Parameter description > Path parameters | TiCDC OpenAPI v1 > Pause a replication task > Example | TiCDC OpenAPI v1 > Resume a replication task | TiCDC OpenAPI v1 > Resume a replication task > Request URI | TiCDC OpenAPI v1 > Resume a replication task > Parameter description | TiCDC OpenAPI v1 > Resume a replication task > Parameter description > Path parameters | TiCDC OpenAPI v1 > Resume a replication task > Example | TiCDC OpenAPI v1 > Query the replication subtask list | TiCDC OpenAPI v1 > Query the replication subtask list > Request URI | TiCDC OpenAPI v1 > Query the replication subtask list > Example | TiCDC OpenAPI v1 > Query a specific replication subtask | TiCDC OpenAPI v1 > Query a specific replication subtask > Request URI | TiCDC OpenAPI v1 > Query a specific replication subtask > Parameter description | TiCDC OpenAPI v1 > Query a specific replication subtask > Parameter description > Path parameters | TiCDC OpenAPI v1 > Query a specific replication subtask > Example | TiCDC OpenAPI v1 > Query the TiCDC service process list | TiCDC OpenAPI v1 > Query the TiCDC service process list > Request URI | TiCDC OpenAPI v1 > Query the TiCDC service process list > Example`
- Source Line Ranges: `263-508`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `openapi`, `changefeed`, `query`, `pause`, `resume`, `processor`, `capture`, `request-uri`, `path-parameters`, `examples`, `state-filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0773_2b97dbad2d`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api.md#query-parameters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d1cb9c032db348381d18d10d309c95945250b95cd0f033e388bc69b6449db989`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api#query-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiCDC OpenAPI v1 endpoints for listing or querying changefeeds, pausing or resuming a changefeed, and querying processors or captures.
- Retrieval Keywords: GET /api/v1/changefeeds, state=normal, state filter all normal stopped error failed finished, GET /api/v1/changefeeds/{changefeed_id}, POST /api/v1/changefeeds/{changefeed_id}/pause, POST /api/v1/changefeeds/{changefeed_id}/resume, GET /api/v1/processors, GET /api/v1/processors/{changefeed_id}/{capture_id}, GET /api/v1/captures, changefeed_id, capture_id, checkpoint_tso, checkpoint_time, processor, capture
- Follow-up Guidance: The content also includes example curl requests and returned fields such as id, state, checkpoint_tso, checkpoint_time, task_status, checkpoint_ts, resolved_ts, is_owner, and address.
- Classification Note: This is reference content because it defines TiCDC OpenAPI request URIs, parameters, response meanings, and examples for changefeed, processor, and capture queries plus pause and resume operations.

## Official Source Content

#### Query parameters

| Parameter name | Description |
| :------ | :---------------------------------------- ----- |
| `state` | When this parameter is specified, the replication status information only of this state is returned.(Optional) |

The value options for `state` are `all`, `normal`, `stopped`, `error`, `failed`, and `finished`.

If this parameter is not specified, the basic information of replication tasks whose state is normal, stopped, or failed is returned by default.
### Example

The following request queries the basic information of all replication tasks whose state is `normal`.

```shell
curl -X GET http://127.0.0.1:8300/api/v1/changefeeds?state=normal
```

```json
[
    {
        "id": "test1",
        "state": "normal",
        "checkpoint_tso": 426921294362574849,
        "checkpoint_time": "2021-08-10 14:04:54.242",
        "error": null
    },
    {
        "id": "test2",
        "state": "normal",
        "checkpoint_tso": 426921294362574849,
        "checkpoint_time": "2021-08-10 14:04:54.242",
        "error": null
    }
]
```

The fields in the returned result above are described as follows:

- id: The ID of the replication task.
- state: The current [state](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-overview#changefeed-state-transfer) of the replication task.
- checkpoint_tso: The TSO representation of the current checkpoint of the replication task.
- checkpoint_time: The formatted time representation of the current checkpoint of the replication task.
- error: The error information of the replication task.
## Query a specific replication task

This API is a synchronous interface. If the request is successful, the detailed information of the specified replication task is returned.
### Request URI

`GET /api/v1/changefeeds/{changefeed_id}`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be queried. |
### Example

The following request queries the detailed information of the replication task with the ID `test1`.

```shell
curl -X GET http://127.0.0.1:8300/api/v1/changefeeds/test1
```

```json
{
    "id": "test1",
    "sink_uri": "blackhole://",
    "create_time": "2021-08-10 11:41:30.642",
    "start_ts": 426919038970232833,
    "target_ts": 0,
    "checkpoint_tso": 426921014615867393,
    "checkpoint_time": "2021-08-10 13:47:07.093",
    "sort_engine": "unified",
    "state": "normal",
    "error": null,
    "error_history": null,
    "creator_version": "",
    "task_status": [
        {
            "capture_id": "d8924259-f52f-4dfb-97a9-c48d26395945",
            "table_ids": [
                63,
                65
            ],
            "table_operations": {}
        }
    ]
}
```
## Pause a replication task

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v1/changefeeds/{changefeed_id}/pause`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be paused. |
### Example

The following request pauses the replication task with the ID `test1`.

```shell
curl -X POST http://127.0.0.1:8300/api/v1/changefeeds/test1/pause
```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Resume a replication task

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v1/changefeeds/{changefeed_id}/resume`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be resumed. |
### Example

The following request resumes the replication task with the ID `test1`.

```shell
curl -X POST http://127.0.0.1:8300/api/v1/changefeeds/test1/resume
```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Query the replication subtask list

This API is a synchronous interface. If the request is successful, the basic information of all replication subtasks (`processor`) is returned.
### Request URI

`GET /api/v1/processors`
### Example

```shell
curl -X GET http://127.0.0.1:8300/api/v1/processors
```

```json
[
    {
        "changefeed_id": "test1",
        "capture_id": "561c3784-77f0-4863-ad52-65a3436db6af"
    }
]
```
## Query a specific replication subtask

This API is a synchronous interface. If the request is successful, the detailed information of the specified replication subtask (`processor`) is returned.
### Request URI

`GET /api/v1/processors/{changefeed_id}/{capture_id}`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The changefeed ID of the replication subtask to be queried. |
| `capture_id` | The capture ID of the replication subtask to be queried. |
### Example

The following request queries the detailed information of a subtask whose `changefeed_id` is `test` and `capture_id` is `561c3784-77f0-4863-ad52-65a3436db6af`. A subtask can be indentifed by `changefeed_id` and `capture_id`.

```shell
curl -X GET http://127.0.0.1:8300/api/v1/processors/test1/561c3784-77f0-4863-ad52-65a3436db6af
```

```json
{
    "checkpoint_ts": 426919123303006208,
    "resolved_ts": 426919123369066496,
    "table_ids": [
        63,
        65
    ],
    "error": null
}
```
## Query the TiCDC service process list

This API is a synchronous interface. If the request is successful, the basic information of all replication processes (`capture`) is returned.
### Request URI

`GET /api/v1/captures`
### Example

```shell
curl -X GET http://127.0.0.1:8300/api/v1/captures
```

```json
[
    {
        "id": "561c3784-77f0-4863-ad52-65a3436db6af",
        "is_owner": true,
        "address": "127.0.0.1:8300"
    }
]
```
