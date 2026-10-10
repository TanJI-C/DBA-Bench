# Query replication task details and completion status APIs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api-v2.md`
- Source Title: `TiCDC OpenAPI v2`
- Source Heading Path: `TiCDC OpenAPI v2 > Query a specific replication task > Parameter description | TiCDC OpenAPI v2 > Query a specific replication task > Parameter description > Path parameter | TiCDC OpenAPI v2 > Query a specific replication task > Example | TiCDC OpenAPI v2 > Query whether a specific replication task is completed | TiCDC OpenAPI v2 > Query whether a specific replication task is completed > Request URI | TiCDC OpenAPI v2 > Query whether a specific replication task is completed > Parameter description | TiCDC OpenAPI v2 > Query whether a specific replication task is completed > Parameter description > Path parameter | TiCDC OpenAPI v2 > Query whether a specific replication task is completed > Examples`
- Source Line Ranges: `749-855`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`, `tikv`
- Topic Tags: `openapi`, `changefeed`, `query`, `sync-status`, `path-parameters`, `examples`, `pd-time`, `error-codes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0771_bfd53af2a7`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api-v2.md#parameter-description`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce0834cbf00cb7718abb7b5fc5c2e4797a3ab433c2f4636cc86d86ea79f31618`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#parameter-description
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api-v2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiCDC OpenAPI v2 endpoints for querying a changefeed’s details or checking whether a specific replication task is synced.
- Retrieval Keywords: GET /api/v2/changefeeds/{changefeed_id}, GET /api/v2/changefeeds/{changefeed_id}/synced, changefeed_id, synced, sink_checkpoint_ts, puller_resolved_ts, last_synced_ts, now_ts, info, error_msg, error_code, [CDC:ErrPDEtcdAPIError]
- Follow-up Guidance: If the sync-status response is false, check the info field together with the other PD time fields to interpret the replication task state.
- Classification Note: This chunk documents reference APIs for a changefeed and its synchronous synced-status query, including example responses and error output.

## Official Source Content

### Parameter description
#### Path parameter

| Parameter name | Description |
| :-------------- | :----------------------------------- |
| `changefeed_id` | The ID of the replication task (changefeed) to be queried. |
### Example

The following request queries the detailed information of the replication task with the ID `test1`.

```shell
curl -X GET http://127.0.0.1:8300/api/v2/changefeeds/test1
```

The meanings of the JSON response body are the same as those in the [Create a replication task](#create-a-replication-task) section. See that section for details.
## Query whether a specific replication task is completed

This API is a synchronous interface. If the request is successful, it returns the synchronization status of the specified replication task (changefeed), including whether the task is completed and additional details.
### Request URI

`GET /api/v2/changefeeds/{changefeed_id}/synced`
### Parameter description
#### Path parameter

| Parameter name  | Description                 |
|:----------------|:----------------------------|
| `changefeed_id` | The ID of the replication task (changefeed) to be queried. |
### Examples

The following request queries the synchronization status of the replication task with the ID `test1`.

```shell
curl -X GET http://127.0.0.1:8300/api/v2/changefeeds/test1/synced
```

**Example 1: The synchronization is completed**

```json
{
  "synced": true,
  "sink_checkpoint_ts": "2023-11-30 15:14:11.015",
  "puller_resolved_ts": "2023-11-30 15:14:12.215",
  "last_synced_ts": "2023-11-30 15:08:35.510",
  "now_ts": "2023-11-30 15:14:11.511",
  "info": "Data syncing is finished"
}
```

The response includes the following fields:

- `synced`: whether this replication task is completed. `true` means the task is completed, and `false` means potential incompleteness. If it is `false`, you need to check both the `info` field and other fields for the specific status.
- `sink_checkpoint_ts`: the checkpoint-ts value of the sink module, in PD time.
- `puller_resolved_ts`: the resolved-ts value of the puller module, in PD time.
- `last_synced_ts`: the commit-ts value of the latest data processed by TiCDC, in PD time.
- `now_ts`: current PD time.
- `info`: supplementary information to assist in determining the synchronization status, especially when `synced` is `false`.

**Example 2: The synchronization is not completed**

```json
{
  "synced": false,
  "sink_checkpoint_ts": "2023-11-30 15:26:31.519",
  "puller_resolved_ts": "2023-11-30 15:26:23.525",
  "last_synced_ts": "2023-11-30 15:24:30.115",
  "now_ts": "2023-11-30 15:26:31.511",
  "info": "The data syncing is not finished, please wait"
}
```

This example shows the response of an ongoing replication task. By checking both `synced` and `info` fields, you can learn that the replication task is not completed yet and further waiting is expected.

**Example 3: The synchronization status needs further check**

```json
{
  "synced":false,
  "sink_checkpoint_ts":"2023-12-13 11:45:13.515",
  "puller_resolved_ts":"2023-12-13 11:45:13.525",
  "last_synced_ts":"2023-12-13 11:45:07.575",
  "now_ts":"2023-12-13 11:50:24.875",
  "info":"Please check whether PD is online and TiKV Regions are all available. If PD is offline or some TiKV regions are not available, it means that the data syncing process is complete. To check whether TiKV regions are all available, you can view 'TiKV-Details' > 'Resolved-Ts' > 'Max Leader Resolved TS gap' on Grafana. If the gap is large, such as a few minutes, it means that some regions in TiKV are unavailable. Otherwise, if the gap is small and PD is online, it means the data syncing is incomplete, so please wait"
}
```

This API enables you to query the synchronization status even when the upstream cluster encounters disasters. In certain situations, you might not be able to directly determine whether the current data replication task of TiCDC is completed or not. In such cases, you can request this API, and then check both the `info` field in the response and the current status of the upstream cluster to determine the specific status.

In this example, `sink_checkpoint_ts` is behind `now_ts` in time, either because TiCDC is still catching up with data replication, or because the PD or TiKV has failed. If this is due to TiCDC still catching up with data replication, it means that the replication task is not completed yet. If this is due to a PD or TiKV failure, it means that the replication task is completed. Therefore, you need to check the `info` field to assist in determining the cluster status.

**Example 4: Query error**

```json
{
  "error_msg": "[CDC:ErrPDEtcdAPIError]etcd api call error: context deadline exceeded",
  "error_code": "CDC:ErrPDEtcdAPIError"
}
```

In cases where PD in the upstream cluster fails for a long period of time, querying this API might return an error similar to the preceding one, which provides no information for further check. Because PD failures directly affect TiCDC data replication, when getting such errors, you can assume that TiCDC has completed the data replication as much as possible, but data loss might still occur in the downstream cluster due to PD failures.
