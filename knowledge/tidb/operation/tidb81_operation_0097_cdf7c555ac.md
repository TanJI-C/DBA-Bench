# DM cluster node inspection and stop APIs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-open-api.md`
- Source Title: `Maintain DM Clusters Using OpenAPI`
- Source Heading Path: `Maintain DM Clusters Using OpenAPI > Get the information of a DM-master node | Maintain DM Clusters Using OpenAPI > Get the information of a DM-master node > Request URI | Maintain DM Clusters Using OpenAPI > Get the information of a DM-master node > Example | Maintain DM Clusters Using OpenAPI > Stop a DM-master node | Maintain DM Clusters Using OpenAPI > Stop a DM-master node > Request URI | Maintain DM Clusters Using OpenAPI > Stop a DM-master node > Example | Maintain DM Clusters Using OpenAPI > Get the information of a DM-worker node | Maintain DM Clusters Using OpenAPI > Get the information of a DM-worker node > Request URI | Maintain DM Clusters Using OpenAPI > Get the information of a DM-worker node > Example | Maintain DM Clusters Using OpenAPI > Stop a DM-worker node | Maintain DM Clusters Using OpenAPI > Stop a DM-worker node > Request URI | Maintain DM Clusters Using OpenAPI > Stop a DM-worker node > Example`
- Source Line Ranges: `92-191`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `cluster-management`, `dm-master`, `dm-worker`, `get`, `delete`, `node-info`, `stop-node`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0097_cdf7c555ac`
- Source ID: `tidb-docs-8.1:dm/dm-open-api.md#get-the-information-of-a-dm-master-node`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a126a21f4427661009744aad64282fbde210d476ffcea014a422412093d06e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-open-api#get-the-information-of-a-dm-master-node
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-open-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the OpenAPI endpoints and example responses for listing DM-master or DM-worker nodes or stopping a specific master or worker node.
- Retrieval Keywords: GET /api/v1/cluster/masters, DELETE /api/v1/cluster/masters/{master-name}, GET /api/v1/cluster/workers, DELETE /api/v1/cluster/workers/{worker-name}, Get the information of a DM-master node, Stop a DM-master node, Get the information of a DM-worker node, Stop a DM-worker node, alive, leader, bound_stage, bound_source_name, status code 204
- Follow-up Guidance: The examples show that successful GET requests return node information fields such as name, addr, alive, leader, bound_stage, and bound_source_name, while successful DELETE requests return status code 204.
- Classification Note: This is operation content because it provides concrete cluster management APIs to inspect DM-master and DM-worker nodes and to stop named nodes.

## Official Source Content

## Get the information of a DM-master node

This API is a synchronous interface. If the request is successful, the information of the corresponding node is returned.
### Request URI

`GET /api/v1/cluster/masters`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/cluster/masters' \
  -H 'accept: application/json'
```

```json
{
  "total": 1,
  "data": [
    {
      "name": "master1",
      "alive": true,
      "leader": true,
      "addr": "127.0.0.1:8261"
    }
  ]
}
```
## Stop a DM-master node

This API is a synchronous interface. If the request is successful, the status code of the returned body is 204.
### Request URI

`DELETE /api/v1/cluster/masters/{master-name}`
### Example

```shell
curl -X 'DELETE' \
  'http://127.0.0.1:8261/api/v1/cluster/masters/master1' \
  -H 'accept: */*'
```
## Get the information of a DM-worker node

This API is a synchronous interface. If the request is successful, the information of the corresponding node is returned.
### Request URI

`GET /api/v1/cluster/workers`
### Example

```shell
curl -X 'GET' \
  'http://127.0.0.1:8261/api/v1/cluster/workers' \
  -H 'accept: application/json'
```

```json
{
  "total": 1,
  "data": [
    {
      "name": "worker1",
      "addr": "127.0.0.1:8261",
      "bound_stage": "bound",
      "bound_source_name": "mysql-01"
    }
  ]
}
```
## Stop a DM-worker node

This API is a synchronous interface. If the request is successful, the status code of the returned body is 204.
### Request URI

 `DELETE /api/v1/cluster/workers/{worker-name}`
### Example

```shell
curl -X 'DELETE' \
  'http://127.0.0.1:8261/api/v1/cluster/workers/worker1' \
  -H 'accept: */*'
```
