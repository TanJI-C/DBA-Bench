# DM query-status command results and task status details

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-query-status.md`
- Source Title: `Query Task Status in TiDB Data Migration`
- Source Heading Path: `Query Task Status in TiDB Data Migration | Query Task Status in TiDB Data Migration > Query result | Query Task Status in TiDB Data Migration > Task status | Query Task Status in TiDB Data Migration > Detailed query result`
- Source Line Ranges: `5-221`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `query-status`, `task-status`, `subtask-status`, `json-output`, `command-usage`, `error-inspection`, `relay-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0228_0df8a8aae5`
- Source ID: `tidb-docs-8.1:dm/dm-query-status.md#query-task-status-in-tidb-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b80d119b6eff82e8aee27f92447a20f99f25179adfbaf18d2f64c87d065091f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-query-status#query-task-status-in-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-query-status.md

## Retrieval Guidance

- Use When: Use this content when you need to understand DM `query-status` output, map subtask states to overall task status, or inspect detailed per-source task information and errors for a named task.
- Retrieval Keywords: query-status, query-status <taskName>, Query Task Status in TiDB Data Migration, taskStatus, subTaskStatus, Task status, subtask status, result, msg, tasks, taskName, sources, sourceStatus, relayStatus, stage, unit, Running, Paused, New, Finished, Stopped, Error - Some error occurred in subtask, Error - Relay status is Error/Paused/Stopped, unresolvedDDLLockID, blockingDDLs, unresolvedGroups, masterBinlog, masterBinlogGtid, syncerBinlog, syncerBinlogGtid, totalRows, totalRps, recentRps, finishedBytes, totalBytes, progress, bps, totalTables, completedTables, finishedRows, estimateTotalRows, ExecSQL, Error 1062: Duplicate entry
- Follow-up Guidance: If any error occurs in a task, the source says to use `query-status <taskName>` to view detailed error information for that task.
- Classification Note: This is reference content because it defines the `query-status` command results, enumerates task status mappings from subtask status, and explains detailed returned fields and example JSON output.

## Official Source Content

# Query Task Status in TiDB Data Migration

This document introduces how to use the `query-status` command to query the task status, and the subtask status of DM.
## Query result

It is recommended that you use `query-status` by the following steps:

1. Use `query-status` to check whether each on-going task is in the normal state.
2. If any error occurs in a task, use the `query-status <taskName>` command to see detailed error information. `<taskName>` in this command indicates the name of the task that encounters the error.

A successful query result is as follows:

```bash
» query-status
```

```json
{
    "result": true,
    "msg": "",
    "tasks": [
        {
            "taskName": "test",
            "taskStatus": "Running",
            "sources": [
                "mysql-replica-01",
                "mysql-replica-02"
            ]
        },
        {
            "taskName": "test2",
            "taskStatus": "Paused",
            "sources": [
                "mysql-replica-01",
                "mysql-replica-02"
            ]
        }
    ]
}
```

Some fields in the query result are described as follows:

- `result`: Whether the query is successful.
- `msg`: The error message returned when the query fails.
- `tasks`: The list of migration tasks. Each task contains the following fields:
    - `taskName`: The name of the task.
    - `taskStatus`: The status of the task. For detailed descriptions of `taskStatus`, refer to [Task status](#task-status).
    - `sources`: The list of upstream MySQL databases.
## Task status

The status of a DM migration task depends on the status of each subtask assigned to DM-worker. For detailed descriptions of subtask status, see [Subtask status](#subtask-status). The table below shows how the subtask status is related to task status.

|  Subtask status in a task | Task status |
| :--- | :--- |
| One subtask is in the `paused` state and error information is returned. | `Error - Some error occurred in subtask` |
| One subtask in the Sync phase is in the `Running` state but its Relay processing unit is not running (in the `Error`/`Paused`/`Stopped` state). | `Error - Relay status is Error/Paused/Stopped` |
| One subtask is in the `Paused` state and no error information is returned. | `Paused` |
| All subtasks are in the `New` state. | `New` |
| All subtasks are in the `Finished` state. | `Finished` |
| All subtasks are in the `Stopped` state. | `Stopped` |
| Other situations | `Running` |
## Detailed query result

```bash
» query-status test
```

```json
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "sourceStatus": {
                "source": "mysql-replica-01",
                "worker": "worker1",
                "result": null,
                "relayStatus": null
            },
            "subTaskStatus": [
                {
                    "name": "test",
                    "stage": "Running",
                    "unit": "Sync",
                    "result": null,
                    "unresolvedDDLLockID": "test-`test`.`t_target`",
                    "sync": {
                        "masterBinlog": "(bin.000001, 3234)",
                        "masterBinlogGtid": "c0149e17-dff1-11e8-b6a8-0242ac110004:1-14",
                        "syncerBinlog": "(bin.000001, 2525)",
                        "syncerBinlogGtid": "",
                        "blockingDDLs": [
                            "USE `test`; ALTER TABLE `test`.`t_target` DROP COLUMN `age`;"
                        ],
                        "unresolvedGroups": [
                            {
                                "target": "`test`.`t_target`",
                                "DDLs": [
                                    "USE `test`; ALTER TABLE `test`.`t_target` DROP COLUMN `age`;"
                                ],
                                "firstPos": "(bin|000001.000001, 3130)",
                                "synced": [
                                    "`test`.`t2`"
                                    "`test`.`t3`"
                                    "`test`.`t1`"
                                ],
                                "unsynced": [
                                ]
                            }
                        ],
                        "synced": false,
                        "totalRows": "12",
                        "totalRps": "1",
                        "recentRps": "1"
                    }
                }
            ]
        },
        {
            "result": true,
            "msg": "",
            "sourceStatus": {
                "source": "mysql-replica-02",
                "worker": "worker2",
                "result": null,
                "relayStatus": null
            },
            "subTaskStatus": [
                {
                    "name": "test",
                    "stage": "Running",
                    "unit": "Load",
                    "result": null,
                    "unresolvedDDLLockID": "",
                    "load": {
                        "finishedBytes": "115",
                        "totalBytes": "452",
                        "progress": "25.44 %",
                        "bps": "2734"
                    }
                }
            ]
        },
        {
            "result": true,
            "sourceStatus": {
                "source": "mysql-replica-03",
                "worker": "worker3",
                "result": null,
                "relayStatus": null
            },
            "subTaskStatus": [
                {
                    "name": "test",
                    "stage": "Paused",
                    "unit": "Load",
                    "result": {
                        "isCanceled": false,
                        "errors": [
                            {
                                "Type": "ExecSQL",
                                "msg": "Error 1062: Duplicate entry '1155173304420532225' for key 'PRIMARY'\n/home/jenkins/workspace/build_dm/go/src/github.com/pingcap/tidb-enterprise-tools/loader/db.go:160: \n/home/jenkins/workspace/build_dm/go/src/github.com/pingcap/tidb-enterprise-tools/loader/db.go:105: \n/home/jenkins/workspace/build_dm/go/src/github.com/pingcap/tidb-enterprise-tools/loader/loader.go:138: file test.t1.sql"
                            }
                        ],
                        "detail": null
                    },
                    "unresolvedDDLLockID": "",
                    "load": {
                        "finishedBytes": "0",
                        "totalBytes": "156",
                        "progress": "0.00 %",
                        "bps": "0"
                    }
                }
            ]
        },
        {
            "result": true,
            "msg": "",
            "sourceStatus": {
                "source": "mysql-replica-04",
                "worker": "worker4",
                "result": null,
                "relayStatus": null
            },
            "subTaskStatus": [
                {
                    "name": "test",
                    "stage": "Running",
                    "unit": "Dump",
                    "result": null,
                    "unresolvedDDLLockID": "",
                    "dump": {
                        "totalTables": "10",
                        "completedTables": "3",
                        "finishedBytes": "2542",
                        "finishedRows": "32",
                        "estimateTotalRows": "563",
                        "progress": "30.52 %",
                        "bps": "445"
                    }
                }
            ]
        },
    ]
}
```

Some fields in the returned result are described as follows:
