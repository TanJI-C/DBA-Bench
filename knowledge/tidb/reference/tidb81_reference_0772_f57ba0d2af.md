# TiCDC OpenAPI v1 overview, error format, node status, and cluster health

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api.md`
- Source Title: `TiCDC OpenAPI v1`
- Source Heading Path: `TiCDC OpenAPI v1 | TiCDC OpenAPI v1 > API error message template | TiCDC OpenAPI v1 > Get the status information of a TiCDC node | TiCDC OpenAPI v1 > Get the status information of a TiCDC node > Request URI | TiCDC OpenAPI v1 > Get the status information of a TiCDC node > Example | TiCDC OpenAPI v1 > Check the health status of a TiCDC cluster | TiCDC OpenAPI v1 > Check the health status of a TiCDC cluster > Request URI | TiCDC OpenAPI v1 > Check the health status of a TiCDC cluster > Example`
- Source Line Ranges: `5-103`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `openapi`, `api`, `deprecation`, `error-codes`, `node-status`, `cluster-health`, `curl`, `json`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0772_f57ba0d2af`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api.md#ticdc-openapi-v1`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8427acc6a96518bb2b579d697e62274876a74d0ad3899822073b616daea2e073`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api#ticdc-openapi-v1
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiCDC OpenAPI v1 overview details, the JSON API error message template, or the status and health endpoints for a TiCDC node or cluster.
- Retrieval Keywords: TiCDC OpenAPI v1, deprecated, TiCDC OpenAPI v2, API error message template, error_msg, error_code, GET /api/v1/status, GET /api/v1/health, status information of a TiCDC node, health status of a TiCDC cluster, is_owner, git_hash, capture ID, 200 OK, curl -X GET http://127.0.0.1:8300/api/v1/status, curl -X GET http://127.0.0.1:8300/api/v1/health
- Follow-up Guidance: The content also lists other TiCDC OpenAPI v1 maintenance operations such as creating, removing, updating, pausing, and resuming replication tasks.
- Classification Note: This is reference content because it documents TiCDC OpenAPI v1 behavior, request URIs, returned JSON fields, and HTTP success responses for status and health queries.

## Official Source Content

# TiCDC OpenAPI v1

> **Note**
>
> TiCDC OpenAPI v1 is deprecated and will be deleted in the future. It is recommended to use [TiCDC OpenAPI v2](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2).

TiCDC provides the OpenAPI feature for querying and operating the TiCDC cluster, which is similar to the feature of [`cdc cli` tool](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed).

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
- [Manually trigger the load balancing of all tables in a replication task](#manually-trigger-the-load-balancing-of-all-tables-in-a-replication-task)
- [Manually schedule a table to another node](#manually-schedule-a-table-to-another-node)
- [Dynamically adjust the log level of the TiCDC server](#dynamically-adjust-the-log-level-of-the-ticdc-server)

The request body and returned value of all APIs are in JSON format. The following sections describe the specific usage of the APIs.

In the following examples, the listening IP address of the TiCDC server is `127.0.0.1` and the port is `8300`. You can bind a specified IP and port via `--addr=ip:port` when starting the TiCDC server.
## API error message template

After sending an API request, if an error occurs, the returned error message is in the following format:

```json
{
    "error_msg": "",
    "error_code": ""
}
```

From the above JSON output, `error_msg` describes the error message and `error_code` is the corresponding error code.
## Get the status information of a TiCDC node

This API is a synchronous interface. If the request is successful, the status information of the corresponding node is returned.
### Request URI

`GET /api/v1/status`
### Example

The following request gets the status information of the TiCDC node whose IP address is `127.0.0.1` and port number is `8300`.

```shell
curl -X GET http://127.0.0.1:8300/api/v1/status
```

```json
{
    "version": "v5.2.0-master-dirty",
    "git_hash": "f191cd00c53fdf7a2b1c9308a355092f9bf8824e",
    "id": "c6a43c16-0717-45af-afd6-8b3e01e44f5d",
    "pid": 25432,
    "is_owner": true
}
```

The fields of the above output are described as follows:

- version: The current TiCDC version number.
- git_hash: The Git hash value.
- id: The capture ID of the node.
- pid: The capture process PID of the node.
- is_owner: Indicates whether the node is an owner.
## Check the health status of a TiCDC cluster

This API is a synchronous interface. If the cluster is healthy, `200 OK` is returned.
### Request URI

`GET /api/v1/health`
### Example

```shell
curl -X GET http://127.0.0.1:8300/api/v1/health
```
