# TiCDC OpenAPI changefeed create, remove, update, and list endpoints

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api.md`
- Source Title: `TiCDC OpenAPI v1`
- Source Heading Path: `TiCDC OpenAPI v1 > Create a replication task | TiCDC OpenAPI v1 > Create a replication task > Request URI | TiCDC OpenAPI v1 > Create a replication task > Parameter description | TiCDC OpenAPI v1 > Create a replication task > Parameter description > Parameters for the request body | TiCDC OpenAPI v1 > Create a replication task > Example | TiCDC OpenAPI v1 > Remove a replication task | TiCDC OpenAPI v1 > Remove a replication task > Request URI | TiCDC OpenAPI v1 > Remove a replication task > Parameter description | TiCDC OpenAPI v1 > Remove a replication task > Parameter description > Path parameters | TiCDC OpenAPI v1 > Remove a replication task > Example | TiCDC OpenAPI v1 > Update the replication configuration | TiCDC OpenAPI v1 > Update the replication configuration > Request URI | TiCDC OpenAPI v1 > Update the replication configuration > Parameter description | TiCDC OpenAPI v1 > Update the replication configuration > Parameter description > Path parameters | TiCDC OpenAPI v1 > Update the replication configuration > Parameter description > Parameters for the request body | TiCDC OpenAPI v1 > Update the replication configuration > Example | TiCDC OpenAPI v1 > Query the replication task list | TiCDC OpenAPI v1 > Query the replication task list > Request URI | TiCDC OpenAPI v1 > Query the replication task list > Parameter description`
- Source Line Ranges: `104-262`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tikv`, `shared`
- Topic Tags: `changefeed`, `replication-task`, `sink-uri`, `filter-rules`, `target-ts`, `mounter`, `dispatchers`, `mq`, `pause-resume`, `list`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0074_7d60903825`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api.md#create-a-replication-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a09773014f22909e9bf34d5d7b987aa9916db457b29c4461ae9eb3090e9177de`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api#create-a-replication-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiCDC OpenAPI v1 endpoints and request parameters for creating, removing, updating, or listing changefeeds and their sink-related configuration.
- Retrieval Keywords: POST /api/v1/changefeeds, DELETE /api/v1/changefeeds/{changefeed_id}, PUT /api/v1/changefeeds/{changefeed_id}, GET /api/v1/changefeeds, Create a replication task, Remove a replication task, Update the replication configuration, Query the replication task list, changefeed_id, sink_uri, target_ts, start_ts, force_replicate, ignore_ineligible_table, filter_rules, ignore_txn_start_ts, mounter_worker_num, sink_config, dispatchers, matcher, protocol, canal-json, open-protocol, avro, debezium, simple, blackhole://, 202 Accepted
- Follow-up Guidance: The source states that to modify the changefeed configuration, follow the steps of pause the replication task, modify the configuration, and resume the replication task.
- Classification Note: This is data_pipeline content because it describes TiCDC replication task (changefeed) lifecycle APIs and sink configuration fields used to define data replication behavior.

## Official Source Content

## Create a replication task

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`POST /api/v1/changefeeds`
### Parameter description

Compared to the optional parameters for creating a replication task using the `cli` command, the optional parameters for creating such task using the API are not as complete. This API supports the following parameters.
#### Parameters for the request body

| Parameter name | Description |
| :------------------------ | :---------------------- ------------------------------- |
| `changefeed_id` | `STRING` type. The ID of the replication task. (Optional) |
| `start_ts` | `UINT64` type. Specifies the start TSO of the changefeed. (Optional) |
| `target_ts` | `UINT64` type. Specifies the target TSO of the changefeed. (Optional) |
| **`sink_uri`** | `STRING` type. The downstream address of the replication task. (**Required**) |
| `force_replicate` | `BOOLEAN` type. Determines whether to forcibly replicate the tables without unique indexes. (Optional) |
| `ignore_ineligible_table` | `BOOLEAN` type. Determines whether to ignore the tables that cannot be replicated. (Optional) |
| `filter_rules` | `STRING` type array. The rules for table schema filtering. (Optional) |
| `ignore_txn_start_ts` | `UINT64` type array. Ignores the transaction of a specified start_ts. (Optional) |
| `mounter_worker_num` | `INT` type. The mounter thread number. (Optional) |
| `sink_config` | The configuration parameters of sink. (Optional) |

The meaning and format of `changefeed_id`, `start_ts`, `target_ts`, and `sink_uri` are the same as those described in the [Use `cdc cli` to create a replication task](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#create-a-replication-task) document. For the detailed description of these parameters, see this document. Note that when you specify the certificate path in `sink_uri`, make sure you have uploaded the corresponding certificate to the corresponding TiCDC server.

Some other parameters in the above table are described further as follows.

`force_replicate`: This parameter defaults to `false`. When it is specified as `true`, TiCDC tries to forcibly replicate tables that do not have a unique index.

`ignore_ineligible_table`: This parameter defaults to `false`. When it is specified as `true`, TiCDC ignores tables that cannot be replicated.

`filter_rules`: The rules for table schema filtering, such as `filter_rules = ['foo*.*','bar*.*']`. For details, see the [Table Filter](https://docs.pingcap.com/tidb/stable/table-filter) document.

`ignore_txn_start_ts`: When this parameter is specified, the specified start_ts is ignored. For example, `ignore-txn-start-ts = [1, 2]`.

`mounter_worker_num`: The thread number of mounter. Mounter is used to decode the data output from TiKV. The default value is `16`.

The configuration parameters of sink are as follows:

```json
{
  "dispatchers":[
    {"matcher":["test1.*", "test2.*"], "dispatcher":"ts"},
    {"matcher":["test3.*", "test4.*"], "dispatcher":"index-value"}
  ],
  "protocol":"canal-json"
}
```

`dispatchers`: For the sink of MQ type, you can use dispatchers to configure the event dispatcher. Four dispatchers are supported: `default`, `ts`, `index-value`, and `table`. The dispatcher rules are as follows:

- `default`: dispatches events in the `table` mode.
- `ts`: uses the commitTs of the row change to create the hash value and dispatch events.
- `index-value`: uses the name and value of the selected HandleKey column to create the hash value and dispatch events.
- `table`: uses the schema name of the table and the table name to create the hash value and dispatch events.

`matcher`: The matching syntax of matcher is the same as the filter rule syntax.

`protocol`: For the sink of MQ type, you can specify the protocol format of the message. Currently the following protocols are supported: `canal-json`, `open-protocol`, `avro`, `debezium`, and `simple`.
### Example

The following request creates a replication task with an ID of `test5` and a `sink_uri` of `blackhole://`.

```shell
curl -X POST -H "'Content-type':'application/json'" http://127.0.0.1:8300/api/v1/changefeeds -d '{"changefeed_id":"test5","sink_uri":"blackhole://"}'
```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Remove a replication task

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.
### Request URI

`DELETE /api/v1/changefeeds/{changefeed_id}`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be removed. |
### Example

The following request removes the replication task with the ID `test1`.

```shell
curl -X DELETE http://127.0.0.1:8300/api/v1/changefeeds/test1
```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Update the replication configuration

This API is an asynchronous interface. If the request is successful, `202 Accepted` is returned. The returned result only means that the server agrees to run the command but does not guarantee that the command will be run successfully.

To modify the changefeed configuration, follow the steps of `pause the replication task -> modify the configuration -> resume the replication task`.
### Request URI

`PUT /api/v1/changefeeds/{changefeed_id}`
### Parameter description
#### Path parameters

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be updated. |
#### Parameters for the request body

Currently, only the following configuration can be modified via the API.

| Parameter name | Description |
| :-------------------- | :-------------------------- --------------------------- |
| `target_ts` | `UINT64` type. Specifies the target TSO of the changefeed. (Optional) |
| `sink_uri` | `STRING` type. The downstream address of the replication task. (Optional) |
| `filter_rules` | `STRING` type array. The rules for table schema filtering. (Optional) |
| `ignore_txn_start_ts` | `UINT64` type array. Ignores the transaction of a specified start_ts. (Optional) |
| `mounter_worker_num` | `INT` type. The mounter thread number. (Optional) |
| `sink_config` | The configuration parameters of sink. (Optional) |

The meanings of the above parameters are the same as those in the [Create a replication task](#create-a-replication-task) section. See that section for details.
### Example

The following request updates the `mounter_worker_num` of the replication task with the ID `test1` to `32`.

```shell
 curl -X PUT -H "'Content-type':'application/json'" http://127.0.0.1:8300/api/v1/changefeeds/test1 -d '{"mounter_worker_num":32}'
```

If the request is successful, `202 Accepted` is returned. If the request fails, an error message and error code are returned.
## Query the replication task list

This API is a synchronous interface. If the request is successful, the basic information of all nodes in the TiCDC cluster is returned.
### Request URI

`GET /api/v1/changefeeds`
### Parameter description
