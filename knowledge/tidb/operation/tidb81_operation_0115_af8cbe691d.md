# Shard-merge replace DDL verification and other binlog commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/handle-failed-ddl-statements.md`
- Source Title: `Handle Failed DDL Statements in TiDB Data Migration`
- Source Heading Path: `Handle Failed DDL Statements in TiDB Data Migration > Usage examples > Replace DDL if the migration gets interrupted > Shard merge scenario | Handle Failed DDL Statements in TiDB Data Migration > Usage examples > Other commands`
- Source Line Ranges: `756-843`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `failed-ddl`, `binlog`, `replace-ddl`, `shard-merge`, `query-status`, `verification`, `command-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0115_af8cbe691d`
- Source ID: `tidb-docs-8.1:dm/handle-failed-ddl-statements.md#shard-merge-scenario`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f6bdfbb527ff1d414031f75cc08e9ed5d4a97275f4aa2d5766abb70eacdaa077`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements#shard-merge-scenario
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/handle-failed-ddl-statements.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether a shard-merge DDL replacement succeeded and when looking for DM binlog command references such as status verification, binlog skip, or binlog replace.
- Retrieval Keywords: query-status output, shard merge scenario, replace DDL, failed DDL statements, binlog replace, binlog skip, unresolvedDDLLockID, blockingDDLs, unresolvedGroups, stage Running, unit Sync, synced true, mysql-replica-01, mysql-replica-02
- Follow-up Guidance: For the usage of other commands of `binlog`, refer to the `binlog skip` and `binlog replace` examples above.
- Classification Note: This is classified as an operation chunk because the content shows command result verification for DM migration status and points to related binlog command usage examples.

## Official Source Content

```
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
                        "unresolvedDDLLockID": "",
                        "sync": {
                            "masterBinlog": "(DESKTOP-T561TSO-bin.000001, 2388)",
                            "masterBinlogGtid": "143bdef3-dd4a-11ea-8b00-00155de45f57:1-10",
                            "syncerBinlog": "(DESKTOP-T561TSO-bin.000001, 2388)",
                            "syncerBinlogGtid": "143bdef3-dd4a-11ea-8b00-00155de45f57:1-4",
                            "blockingDDLs": [
                            ],
                            "unresolvedGroups": [
                            ],
                            "unresolvedGroups": [
                            ],
                            "synced": true,
                            "binlogType": "remote",
                            "totalRows": "4",
                            "totalRps": "0",
                            "recentRps": "0"
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
                        "unit": "Sync",
                        "result": null,
                        "unresolvedDDLLockID": "",
                        "sync": {
                            "masterBinlog": "(DESKTOP-T561TSO-bin.000001, 2388)",
                            "masterBinlogGtid": "143bdef3-dd4a-11ea-8b00-00155de45f57:1-10",
                            "syncerBinlog": "(DESKTOP-T561TSO-bin.000001, 2388)",
                            "syncerBinlogGtid": "143bdef3-dd4a-11ea-8b00-00155de45f57:1-4",
                            "blockingDDLs": [
                            ],
                            "unresolvedGroups": [
                            ],
                            "unresolvedGroups": [
                            ],
                            "synced": try,
                            "binlogType": "remote",
                            "totalRows": "4",
                            "totalRps": "0",
                            "recentRps": "0"
                        }
                    }
                ]
            }
        ]
    }
    ```

    </details>

    You can see that the task runs normally with no error and all four wrong DDL statements are replaced.
### Other commands

For the usage of other commands of `binlog`, refer to the `binlog skip` and `binlog replace` examples above.
