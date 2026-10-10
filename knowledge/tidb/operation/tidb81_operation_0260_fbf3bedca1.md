# Query captures, evict owner, and adjust TiCDC log level APIs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api-v2.md`
- Source Title: `TiCDC OpenAPI v2`
- Source Heading Path: `TiCDC OpenAPI v2 > Query the TiCDC service process list | TiCDC OpenAPI v2 > Query the TiCDC service process list > Request URI | TiCDC OpenAPI v2 > Query the TiCDC service process list > Example | TiCDC OpenAPI v2 > Evict an owner node | TiCDC OpenAPI v2 > Evict an owner node > Request URI | TiCDC OpenAPI v2 > Evict an owner node > Example | TiCDC OpenAPI v2 > Dynamically adjust the log level of the TiCDC server | TiCDC OpenAPI v2 > Dynamically adjust the log level of the TiCDC server > Request URI | TiCDC OpenAPI v2 > Dynamically adjust the log level of the TiCDC server > Request parameter | TiCDC OpenAPI v2 > Dynamically adjust the log level of the TiCDC server > Request parameter > Parameter for the request body | TiCDC OpenAPI v2 > Dynamically adjust the log level of the TiCDC server > Example`
- Source Line Ranges: `996-1071`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `openapi`, `capture`, `owner-election`, `owner-resign`, `log-level`, `zap`, `server-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0260_fbf3bedca1`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api-v2.md#query-the-ticdc-service-process-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe7bb0f484d6bb0e79e61beffc5071149618f56701e2d5c9f6b764422e0d66f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#query-the-ticdc-service-process-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api-v2.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiCDC OpenAPI v2 endpoints for listing captures, resigning the owner, or changing the TiCDC server log level.
- Retrieval Keywords: GET /api/v2/captures, capture, is_owner, address, POST /api/v2/owner/resign, owner/resign, POST /api/v2/log, log_level, debug, info, warn, error, dpanic, panic, fatal, zap
- Follow-up Guidance: If you change the server log level, the request body uses the log_level field.
- Classification Note: This chunk documents TiCDC service-process queries, owner resignation, and log-level adjustment APIs.

## Official Source Content

## Query the TiCDC service process list

This API is a synchronous interface. If the request is successful, the basic information of all replication processes (`capture`) is returned.
### Request URI

`GET /api/v2/captures`
### Example

```shell
curl -X GET http://127.0.0.1:8300/api/v2/captures
```

```json
{
  "total": 1,
  "items": [
    {
      "id": "d2912e63-3349-447c-90ba-72a4e04b5e9e",
      "is_owner": true,
      "address": "127.0.0.1:8300"
    }
  ]
}
```

The parameters are described as follows:

- `id`: the capture ID.
- `is_owner`: whether the capture is the owner.
- `address`: the address of the capture.
## Evict an owner node

This API is an asynchronous interface. If the request is successful, `200 OK` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v2/owner/resign`
### Example

The following request evicts the current owner node of TiCDC and triggers a new round of elections to generate a new owner node.

```shell
curl -X POST http://127.0.0.1:8300/api/v2/owner/resign
```

If the request is successful, `200 OK` is returned. If the request fails, an error message and error code are returned.
## Dynamically adjust the log level of the TiCDC server

This API is a synchronous interface. If the request is successful, `200 OK` is returned.
### Request URI

`POST /api/v2/log`
### Request parameter
#### Parameter for the request body

| Parameter name | Description |
| :---------- | :----------------- |
| `log_level` | The log level you want to set. |

`log_level` supports the [log levels provided by zap](https://godoc.org/go.uber.org/zap#UnmarshalText): "debug", "info", "warn", "error", "dpanic" , "panic", and "fatal".
### Example

```shell
curl -X POST -H "Content-type: application/json" http://127.0.0.1:8300/api/v2/log -d '{"log_level":"debug"}'
```

If the request is successful, `200 OK` is returned. If the request fails, an error message and error code are returned.
