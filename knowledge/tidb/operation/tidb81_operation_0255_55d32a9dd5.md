# Create and query TiCDC changefeeds

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-manage-changefeed.md`
- Source Title: `Manage Changefeeds`
- Source Heading Path: `Manage Changefeeds | Manage Changefeeds > Create a replication task | Manage Changefeeds > Query the replication task list | Manage Changefeeds > Query a specific replication task`
- Source Line Ranges: `5-150`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tikv`
- Topic Tags: `changefeed`, `create`, `list`, `query`, `checkpoint`, `state`, `resolved-ts`, `admin-job-type`, `processor`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0255_55d32a9dd5`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-manage-changefeed.md#manage-changefeeds`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ba549808d35f961b80d1afe2585ef44b18aa85cf308fc1e29a7380df3fbf840`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#manage-changefeeds
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-manage-changefeed.md

## Retrieval Guidance

- Use When: Use this when you need TiCDC `cdc cli changefeed create`, `list`, or `query` examples and the meanings of `state`, `checkpoint`, `resolved-ts`, `checkpoint-ts`, or `admin-job-type`.
- Retrieval Keywords: cdc cli changefeed create, cdc cli changefeed list, cdc cli changefeed query, changefeed list, changefeed query, checkpoint, resolved-ts, checkpoint-ts, admin-job-type, processor, state, simple-replication-task
- Follow-up Guidance: Use the corresponding `changefeed query` or `changefeed list` output to inspect the changefeed configuration and replication status.
- Classification Note: This chunk is about creating and querying TiCDC changefeeds, including the list and query outputs and the documented field meanings.

## Official Source Content

# Manage Changefeeds

This document describes how to create and manage TiCDC changefeeds by using the TiCDC command-line tool `cdc cli`. You can also manage changefeeds via the HTTP interface of TiCDC. For details, see [TiCDC OpenAPI](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api).
## Create a replication task

Run the following command to create a replication task:

```shell
cdc cli changefeed create --server=http://10.0.10.25:8300 --sink-uri="mysql://root:123456@127.0.0.1:3306/" --changefeed-id="simple-replication-task"
```

```shell
Create changefeed successfully!
ID: simple-replication-task
Info: {"upstream_id":7178706266519722477,"namespace":"default","id":"simple-replication-task","sink_uri":"mysql://root:xxxxx@127.0.0.1:4000/?time-zone=","create_time":"2024-12-26T15:05:46.679218+08:00","start_ts":438156275634929669,"engine":"unified","config":{"case_sensitive":false,"force_replicate":false,"ignore_ineligible_table":false,"check_gc_safe_point":true,"enable_sync_point":true,"bdr_mode":false,"sync_point_interval":30000000000,"sync_point_retention":3600000000000,"filter":{"rules":["test.*"],"event_filters":null},"mounter":{"worker_num":16},"sink":{"protocol":"","schema_registry":"","csv":{"delimiter":",","quote":"\"","null":"\\N","include_commit_ts":false},"column_selectors":null,"transaction_atomicity":"none","encoder_concurrency":16,"terminator":"\r\n","date_separator":"none","enable_partition_separator":false},"consistent":{"level":"none","max_log_size":64,"flush_interval":2000,"storage":""}},"state":"normal","creator_version":"v8.1.2"}
```
## Query the replication task list

Run the following command to query the replication task list:

```shell
cdc cli changefeed list --server=http://10.0.10.25:8300
```

```shell
[{
    "id": "simple-replication-task",
    "summary": {
      "state": "normal",
      "tso": 417886179132964865,
      "checkpoint": "2020-07-07 16:07:44.881",
      "error": null
    }
}]
```

- `checkpoint` indicates that TiCDC has already replicated data before this time point to the downstream.
- `state` indicates the state of the replication task.
    - `normal`: The replication task runs normally.
    - `stopped`: The replication task is stopped (manually paused).
    - `error`: The replication task is stopped (by an error).
    - `removed`: The replication task is removed. Tasks of this state are displayed only when you have specified the `--all` option. To see these tasks when this option is not specified, run the `changefeed query` command.
    - `finished`: The replication task is finished (data is replicated to the `target-ts`). Tasks of this state are displayed only when you have specified the `--all` option. To see these tasks when this option is not specified, run the `changefeed query` command.
## Query a specific replication task

To query a specific replication task, run the `changefeed query` command. The query result includes the task information and the task state. You can specify the `--simple` or `-s` argument to simplify the query result that will only include the basic replication state and the checkpoint information. If you do not specify this argument, detailed task configuration, replication states, and replication table information are output.

```shell
cdc cli changefeed query -s --server=http://10.0.10.25:8300 --changefeed-id=simple-replication-task
```

```shell
{
 "state": "normal",
 "tso": 419035700154597378,
 "checkpoint": "2020-08-27 10:12:19.579",
 "error": null
}
```

In the preceding command and result:

+ `state` is the replication state of the current changefeed. Each state must be consistent with the state in `changefeed list`.
+ `tso` represents the largest transaction TSO in the current changefeed that has been successfully replicated to the downstream.
+ `checkpoint` represents the corresponding time of the largest transaction TSO in the current changefeed that has been successfully replicated to the downstream.
+ `error` records whether an error has occurred in the current changefeed.

```shell
cdc cli changefeed query --server=http://10.0.10.25:8300 --changefeed-id=simple-replication-task
```

```shell
{
  "info": {
    "sink-uri": "mysql://127.0.0.1:3306/?max-txn-row=20\u0026worker-count=4",
    "opts": {},
    "create-time": "2020-08-27T10:33:41.687983832+08:00",
    "start-ts": 419036036249681921,
    "target-ts": 0,
    "admin-job-type": 0,
    "sort-engine": "unified",
    "sort-dir": ".",
    "config": {
      "case-sensitive": false,
      "filter": {
        "rules": [
          "*.*"
        ],
        "ignore-txn-start-ts": null,
        "ddl-allow-list": null
      },
      "mounter": {
        "worker-num": 16
      },
      "sink": {
        "dispatchers": null,
      },
      "scheduler": {
        "type": "table-number",
        "polling-time": -1
      }
    },
    "state": "normal",
    "history": null,
    "error": null
  },
  "status": {
    "resolved-ts": 419036036249681921,
    "checkpoint-ts": 419036036249681921,
    "admin-job-type": 0
  },
  "count": 0,
  "task-status": [
    {
      "capture-id": "97173367-75dc-490c-ae2d-4e990f90da0f",
      "status": {
        "tables": {
          "47": {
            "start-ts": 419036036249681921
          }
        },
        "operation": null,
        "admin-job-type": 0
      }
    }
  ]
}
```

In the preceding command and result:

- `info` is the replication configuration of the queried changefeed.
- `status` is the replication state of the queried changefeed.
    - `resolved-ts`: The largest transaction `TS` in the current changefeed. Note that this `TS` has been successfully sent from TiKV to TiCDC.
    - `checkpoint-ts`: The largest transaction `TS` in the current `changefeed`. Note that this `TS` has been successfully written to the downstream.
    - `admin-job-type`: The status of a changefeed:
        - `0`: The state is normal.
        - `1`: The task is paused. When the task is paused, all replicated `processor`s exit. The configuration and the replication status of the task are retained, so you can resume the task from `checkpoint-ts`.
        - `2`: The task is resumed. The replication task resumes from `checkpoint-ts`.
        - `3`: The task is removed. When the task is removed, all replicated `processor`s are ended, and the configuration information of the replication task is cleared up. Only the replication status is retained for later queries.
- `task-status` indicates the state of each replication sub-task in the queried changefeed.
