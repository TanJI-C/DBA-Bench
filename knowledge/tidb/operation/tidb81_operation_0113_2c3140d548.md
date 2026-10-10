# Replace failed DDL in non-shard merge migration

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/handle-failed-ddl-statements.md`
- Source Title: `Handle Failed DDL Statements in TiDB Data Migration`
- Source Heading Path: `Handle Failed DDL Statements in TiDB Data Migration > Usage examples > Replace DDL if the migration gets interrupted > Non-shard-merge scenario`
- Source Line Ranges: `472-591`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `failed-ddl`, `ddl-replacement`, `query-status`, `binlog-replace`, `migration-interruption`, `non-shard-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0113_2c3140d548`
- Source ID: `tidb-docs-8.1:dm/handle-failed-ddl-statements.md#non-shard-merge-scenario`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d0681e7757e7566457d638cd400af8c9e302e803f6a62f6638d9c9100cd444af`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements#non-shard-merge-scenario
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/handle-failed-ddl-statements.md

## Retrieval Guidance

- Use When: Use this chunk when a DM non-shard-merge migration is interrupted by an unsupported upstream DDL such as adding a column with a UNIQUE constraint and you need the exact replacement and status-check commands.
- Retrieval Keywords: Non-shard-merge scenario, query-status, binlog replace test, ALTER TABLE `db1`.`tbl1` ADD COLUMN new_col INT UNIQUE, cannot track DDL, [ddl:8200]unsupported add column 'new_col' constraint UNIQUE KEY when altering 'db1.tbl1', ALTER TABLE `db1`.`tbl1` ADD COLUMN `new_col` INT;ALTER TABLE `db1`.`tbl1` ADD UNIQUE(`new_col`), migration task gets interrupted
- Follow-up Guidance: After replacing the DDL, `query-status test` shows the subtask stage as `Running`, unit `Sync`, and `synced: true`, indicating the replacement DDLs execute successfully.
- Classification Note: This is an operation example for DM that handles a failed DDL in a self-managed non-shard-merge migration by replacing one unsupported statement with two equivalent DDL statements.

## Official Source Content

#### Non-shard-merge scenario

Assume that you need to migrate the upstream table `db1.tbl1` to the downstream TiDB. The initial table schema is:

```sql
SHOW CREATE TABLE db1.tbl1;
```

```SQL
+-------+-----------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                              |
+-------+-----------------------------------------------------------------------------------------------------------+
| tb    | CREATE TABLE `tbl1` (
  `id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_bin |
+-------+-----------------------------------------------------------------------------------------------------------+
```

Now, perform the following DDL operation in the upstream to add a new column with the UNIQUE constraint:

```sql
ALTER TABLE `db1`.`tbl1` ADD COLUMN new_col INT UNIQUE;
```

Because this DDL statement is not supported by TiDB, the migration task gets interrupted. Execute the `query-status` command, and you can see the following error:

```
{
    "Message": "cannot track DDL: ALTER TABLE `db1`.`tbl1` ADD COLUMN `new_col` INT UNIQUE KEY",
    "RawCause": "[ddl:8200]unsupported add column 'new_col' constraint UNIQUE KEY when altering 'db1.tbl1'",
}
```

You can replace this DDL statement with two equivalent DDL statements. The steps are as follows:

1. Replace the wrong DDL statement by the following command:

    ```bash
    » binlog replace test "ALTER TABLE `db1`.`tbl1` ADD COLUMN `new_col` INT;ALTER TABLE `db1`.`tbl1` ADD UNIQUE(`new_col`)";
    ```

    ```
    {
        "result": true,
        "msg": "",
        "sources": [
            {
                "result": true,
                "msg": "",
                "source": "mysql-replica-01",
                "worker": "worker1"
            }
        ]
    }
    ```

2. Use `query-status <task-name>` to view the task status:

    ```bash
    » query-status test
    ```

    <details><summary> See the execution result.</summary>

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
                            "synced": true,
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

    You can see that the task runs normally and the wrong DDL statement is replaced by new DDL statements that execute successfully.
