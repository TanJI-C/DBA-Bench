# Owner control, table scheduling, and log level APIs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api.md`
- Source Title: `TiCDC OpenAPI v1`
- Source Heading Path: `TiCDC OpenAPI v1 > Evict an owner node | TiCDC OpenAPI v1 > Evict an owner node > Request URI | TiCDC OpenAPI v1 > Evict an owner node > Example | TiCDC OpenAPI v1 > Manually trigger the load balancing of all tables in a replication task | TiCDC OpenAPI v1 > Manually trigger the load balancing of all tables in a replication task > Request URI | TiCDC OpenAPI v1 > Manually trigger the load balancing of all tables in a replication task > Parameter description | TiCDC OpenAPI v1 > Manually trigger the load balancing of all tables in a replication task > Parameter description > Path parameters | TiCDC OpenAPI v1 > Manually trigger the load balancing of all tables in a replication task > Example | TiCDC OpenAPI v1 > Manually schedule a table to another node | TiCDC OpenAPI v1 > Manually schedule a table to another node > Request URI | TiCDC OpenAPI v1 > Manually schedule a table to another node > Parameter description | TiCDC OpenAPI v1 > Manually schedule a table to another node > Parameter description > Path parameters | TiCDC OpenAPI v1 > Manually schedule a table to another node > Parameter description > Parameters for the request body | TiCDC OpenAPI v1 > Manually schedule a table to another node > Example | TiCDC OpenAPI v1 > Dynamically adjust the log level of the TiCDC server | TiCDC OpenAPI v1 > Dynamically adjust the log level of the TiCDC server > Request URI | TiCDC OpenAPI v1 > Dynamically adjust the log level of the TiCDC server > Request parameters | TiCDC OpenAPI v1 > Dynamically adjust the log level of the TiCDC server > Request parameters > Parameters for the request body | TiCDC OpenAPI v1 > Dynamically adjust the log level of the TiCDC server > Example`
- Source Line Ranges: `509-620`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `openapi`, `owner`, `resign`, `rebalance`, `move-table`, `capture`, `log-level`, `scheduling`, `asynchronous`, `request-body`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0774_eb21369c19`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api.md#evict-an-owner-node`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `092e1d9582ae8e43c96910283e5882d275eddab181721dd66766693c0a33b5d0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api#evict-an-owner-node
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiCDC OpenAPI v1 endpoints for owner resign, changefeed table rebalance or move_table scheduling, and dynamic log level changes.
- Retrieval Keywords: POST /api/v1/owner/resign, evict an owner node, POST /api/v1/changefeeds/{changefeed_id}/tables/rebalance_table, rebalance_table, POST /api/v1/changefeeds/{changefeed_id}/tables/move_table, move_table, target_capture_id, table_id, POST /api/v1/log, log_level, debug info warn error dpanic panic fatal, 202 Accepted, 202 OK
- Follow-up Guidance: The content includes request body parameters for move_table and log_level, example curl commands, and notes that failed requests return an error message and error code.
- Classification Note: This is reference content because it specifies TiCDC OpenAPI endpoints, path and body parameters, supported log levels, and success semantics for owner control, table scheduling, and log configuration.

## Official Source Content

## Evict an owner node

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v1/owner/resign`
### Example

The following request evicts the current owner node of TiCDC and triggers a new round of elections to generate a new owner node.

```shell
curl -X POST http://127.0.0.1:8300/api/v1/owner/resign
```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Manually trigger the load balancing of all tables in a replication task

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v1/changefeeds/{changefeed_id}/tables/rebalance_table`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be scheduled. |
### Example

The following request triggers the load balancing of all tables in the changefeed with the ID `test1`.

```shell
 curl -X POST http://127.0.0.1:8300/api/v1/changefeeds/test1/tables/rebalance_table
```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Manually schedule a table to another node

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v1/changefeeds/{changefeed_id}/tables/move_table`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be scheduled. |
#### Parameters for the request body

| Parameter name | Description |
| :------------------ | :------------------ |
| `target_capture_id` | The ID of the target capture. |
| `table_id` | The ID of the table to be scheduled. |
### Example

The following request schedules the table with the ID `49` in the changefeed with the ID `test1` to the capture with the ID `6f19a6d9-0f8c-4dc9-b299-3ba7c0f216f5`.

```shell
curl -X POST -H "'Content-type':'application/json'" http://127.0.0.1:8300/api/v1/changefeeds/changefeed-test1/tables/move_table -d '{"capture_id":"6f19a6d9-0f8c-4dc9-b299-3ba7c0f216f5","table_id":49}'

```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Dynamically adjust the log level of the TiCDC server

This API is a synchronous interface. If the request is successful, `202 OK` is returned.
### Request URI

`POST /api/v1/log`
### Request parameters
#### Parameters for the request body

| Parameter name | Description |
| :---------- | :----------------- |
| `log_level` | The log level you want to set. |

`log_level` supports the [log levels provided by zap](https://godoc.org/go.uber.org/zap#UnmarshalText): "debug", "info", "warn", "error", "dpanic" , "panic", and "fatal".
### Example

```shell
curl -X POST -H "'Content-type':'application/json'" http://127.0.0.1:8300/api/v1/log -d '{"log_level":"debug"}'

```

If the request is successful, `202 OK` is returned. If the request fails, an error message and error code are returned.
