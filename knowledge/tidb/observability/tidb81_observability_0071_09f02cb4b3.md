# PD health, hot spot, and label inspection commands

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `health` | PD Control User Guide > Command > `hot [read | write | store|  history <start_time> <end_time> [<key> <value>]]` | PD Control User Guide > Command > `label [store <name> <value>]``
- Source Line Ranges: `355-441`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `pd-ctl`, `health`, `hotspot`, `history`, `labels`, `stores`, `cluster-state`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0071_09f02cb4b3`
- Source ID: `tidb-docs-8.1:pd-control.md#health`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9480d1a847119ef722ff12f9f42d3ba21fea0807b9e0062e34d43ad569572ce8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#health
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for pd-ctl commands to inspect cluster health, current or historical hot spot information, or store labels.
- Retrieval Keywords: health, hot read, hot write, hot store, hot history, history_hot_region, hot_region_type, region_id, store_id, peer_id, is_leader, is_learner, start_time end_time milliseconds, label, label store zone cn, cluster health information, hot spot information, label information of the cluster
- Follow-up Guidance: The `hot history` command supports additional filter conditions such as `hot_region_type`, `region_id`, `store_id`, `peer_id`, `is_leader`, and `is_learner` within a specified start and end time.
- Classification Note: This is classified as observability because the commands in the content are used to view PD member health, hot spot activity, hotspot history, and label state in the cluster.

## Official Source Content

### `health`

Use this command to view the health information of the cluster.

Usage:

```bash
>> health                                // Display the health information
[
  {
    "name": "pd",
    "member_id": 13195394291058371180,
    "client_urls": [
      "http://127.0.0.1:2379"
      ......
    ],
    "health": true
  }
  ......
]
```
### `hot [read | write | store|  history <start_time> <end_time> [<key> <value>]]`

Use this command to view the hot spot information of the cluster.

Usage:

```bash
>> hot read                                // Display hot spot for the read operation
>> hot write                               // Display hot spot for the write operation
>> hot store                               // Display hot spot for all the read and write operations
>> hot history 1629294000000 1631980800000 // Display history hot spot for the specified period (milliseconds). 1629294000000 is the start time and 1631980800000 is the end time.
{
  "history_hot_region": [
    {
      "update_time": 1630864801948,
      "region_id": 103,
      "peer_id": 1369002,
      "store_id": 3,
      "is_leader": true,
      "is_learner": false,
      "hot_region_type": "read",
      "hot_degree": 152,
      "flow_bytes": 0,
      "key_rate": 0,
      "query_rate": 305,
      "start_key": "7480000000000000FF5300000000000000F8",
      "end_key": "7480000000000000FF5600000000000000F8"
    },
    ...
  ]
}
>> hot history 1629294000000 1631980800000 hot_region_type read region_id 1,2,3 store_id 1,2,3 peer_id 1,2,3 is_leader true is_learner true // Display history hotspot for the specified period with more conditions
{
  "history_hot_region": [
    {
      "update_time": 1630864801948,
      "region_id": 103,
      "peer_id": 1369002,
      "store_id": 3,
      "is_leader": true,
      "is_learner": false,
      "hot_region_type": "read",
      "hot_degree": 152,
      "flow_bytes": 0,
      "key_rate": 0,
      "query_rate": 305,
      "start_key": "7480000000000000FF5300000000000000F8",
      "end_key": "7480000000000000FF5600000000000000F8"
    },
    ...
  ]
}
```
### `label [store <name> <value>]`

Use this command to view the label information of the cluster.

Usage:

```bash
>> label                                // Display all labels
>> label store zone cn                  // Display all stores including the "zone":"cn" label
```
