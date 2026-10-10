# Pause or resume changefeeds and query processors APIs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api-v2.md`
- Source Title: `TiCDC OpenAPI v2`
- Source Heading Path: `TiCDC OpenAPI v2 > Pause a replication task | TiCDC OpenAPI v2 > Pause a replication task > Request URI | TiCDC OpenAPI v2 > Pause a replication task > Parameter description | TiCDC OpenAPI v2 > Pause a replication task > Parameter description > Path parameter | TiCDC OpenAPI v2 > Pause a replication task > Example | TiCDC OpenAPI v2 > Resume a replication task | TiCDC OpenAPI v2 > Resume a replication task > Request URI | TiCDC OpenAPI v2 > Resume a replication task > Parameter description | TiCDC OpenAPI v2 > Resume a replication task > Parameter description > Path parameter | TiCDC OpenAPI v2 > Resume a replication task > Parameter description > Parameters for the request body | TiCDC OpenAPI v2 > Resume a replication task > Example | TiCDC OpenAPI v2 > Query the replication subtask list | TiCDC OpenAPI v2 > Query the replication subtask list > Request URI | TiCDC OpenAPI v2 > Query the replication subtask list > Example | TiCDC OpenAPI v2 > Query a specific replication subtask | TiCDC OpenAPI v2 > Query a specific replication subtask > Request URI | TiCDC OpenAPI v2 > Query a specific replication subtask > Parameter descriptions | TiCDC OpenAPI v2 > Query a specific replication subtask > Parameter descriptions > Path parameters | TiCDC OpenAPI v2 > Query a specific replication subtask > Example`
- Source Line Ranges: `856-995`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `openapi`, `changefeed`, `pause`, `resume`, `checkpoint-tso`, `processor`, `subtask`, `capture-id`, `path-parameters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0259_694e0ae7e3`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api-v2.md#pause-a-replication-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cdd5f350d7fe5405770edb84c265ca573b6f13e27b0d5fa98b338eaec12a4a5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#pause-a-replication-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api-v2.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiCDC OpenAPI v2 operations for pausing or resuming a changefeed, or for listing and inspecting replication subtasks and their processors.
- Retrieval Keywords: POST /api/v2/changefeeds/{changefeed_id}/pause, POST /api/v2/changefeeds/{changefeed_id}/resume, overwrite_checkpoint_ts, GET /api/v2/processors, GET /api/v2/processors/{changefeed_id}/{capture_id}, processor, capture_id, table_ids
- Follow-up Guidance: If you resume a replication task, the request body can include overwrite_checkpoint_ts as the checkpoint TSO to reassign.
- Classification Note: This chunk covers TiCDC operation APIs for pausing, resuming, and querying processor subtask information.

## Official Source Content

## Pause a replication task

This API pauses a replication task. If the request is successful, `200 OK` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v2/changefeeds/{changefeed_id}/pause`
### Parameter description
#### Path parameter

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be paused. |
### Example

The following request pauses the replication task with the ID `test1`.

```shell
curl -X POST http://127.0.0.1:8300/api/v2/changefeeds/test1/pause
```

If the request is successful, `200 OK` is returned. If the request fails, an error message and error code are returned.
## Resume a replication task

This API resumes a replication task. If the request is successful, `200 OK` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v2/changefeeds/{changefeed_id}/resume`
### Parameter description
#### Path parameter

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be resumed. |
#### Parameters for the request body

```json
{
  "overwrite_checkpoint_ts": 0
}
```

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `overwrite_checkpoint_ts` | `UINT64` type. Reassign a checkpoint TSO when resuming a replication task (changefeed). |
### Example

The following request resumes the replication task with the ID `test1`.

```shell
curl -X POST http://127.0.0.1:8300/api/v2/changefeeds/test1/resume -d '{}'
```

If the request is successful, `200 OK` is returned. If the request fails, an error message and error code are returned.
## Query the replication subtask list

This API is a synchronous interface. If the request is successful, the basic information of all replication subtasks (`processor`) is returned.
### Request URI

`GET /api/v2/processors`
### Example

```shell
curl -X GET http://127.0.0.1:8300/api/v2/processors
```

```json
{
  "total": 3,
  "items": [
    {
      "changefeed_id": "test2",
      "capture_id": "d2912e63-3349-447c-90ba-72a4e04b5e9e"
    },
    {
      "changefeed_id": "test1",
      "capture_id": "d2912e63-3349-447c-90ba-72a4e04b5e9e"
    },
    {
      "changefeed_id": "test",
      "capture_id": "d2912e63-3349-447c-90ba-72a4e04b5e9e"
    }
  ]
}
```

The parameters are described as follows:

- `changefeed_id`: the changefeed ID.
- `capture_id`: the capture ID.
## Query a specific replication subtask

This API is a synchronous interface. If the request is successful, the detailed information of the specified replication subtask (`processor`) is returned.
### Request URI

`GET /api/v2/processors/{changefeed_id}/{capture_id}`
### Parameter descriptions
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The changefeed ID of the replication subtask to be queried. |
| `capture_id` | The capture ID of the replication subtask to be queried. |
### Example

The following request queries the detailed information of a subtask whose `changefeed_id` is `test` and `capture_id` is `561c3784-77f0-4863-ad52-65a3436db6af`. A subtask can be identified by `changefeed_id` and `capture_id`.

```shell
curl -X GET http://127.0.0.1:8300/api/v2/processors/test/561c3784-77f0-4863-ad52-65a3436db6af
```

```json
{
  "table_ids": [
    80
  ]
}
```

The parameter is described as follows:

- `table_ids`: The table ID to be replicated on this capture.
