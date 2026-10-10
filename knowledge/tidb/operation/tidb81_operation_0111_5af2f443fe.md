# Skip failed DDL in a non-shard-merge migration scenario

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/handle-failed-ddl-statements.md`
- Source Title: `Handle Failed DDL Statements in TiDB Data Migration`
- Source Heading Path: `Handle Failed DDL Statements in TiDB Data Migration > Usage examples > Skip DDL if the migration gets interrupted > Non-shard-merge scenario`
- Source Line Ranges: `115-232`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `failed-ddl`, `skip`, `non-shard-merge`, `query-status`, `resume-migration`, `unsupported-ddl`, `schema-change`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0111_5af2f443fe`
- Source ID: `tidb-docs-8.1:dm/handle-failed-ddl-statements.md#non-shard-merge-scenario`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4c9a9182b3075b5f5bf01ecb25f3ce0e7c6af4548ff3a8c041063767132dcd35`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements#non-shard-merge-scenario
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/handle-failed-ddl-statements.md

## Retrieval Guidance

- Use When: Use this chunk when a non-shard-merge DM task is interrupted by an unsupported ALTER TABLE on db1.tbl1 and you need the exact skip example, error, and post-check with query-status.
- Retrieval Keywords: Non-shard-merge scenario, db1.tbl1, SHOW CREATE TABLE db1.tbl1, ALTER TABLE db1.tbl1 CHANGE c2 c2 DECIMAL (10, 3);, ERROR 8200 (HY000): Unsupported modify column: can't change decimal column precision, binlog skip test, query-status test, mysql-replica-01, worker1, stage Running, unit Sync
- Follow-up Guidance: The source shows verifying recovery by running query-status <task-name> and checking that the subtask stage is Running and the wrong DDL is skipped.
- Classification Note: This is classified as an operation chunk because it provides a concrete DM procedure for skipping a failed DDL in a non-shard-merge migration and validating that the task resumes normally.

## Official Source Content

#### Non-shard-merge scenario

Assume that you need to migrate the upstream table `db1.tbl1` to the downstream TiDB. The initial table schema is:

```sql
SHOW CREATE TABLE db1.tbl1;
```

```sql
+-------+--------------------------------------------------+
| Table | Create Table                                     |
+-------+--------------------------------------------------+
| tbl1  | CREATE TABLE `tbl1` (
  `c1` int(11) NOT NULL,
  `c2` decimal(11,3) DEFAULT NULL,
  PRIMARY KEY (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 |
+-------+--------------------------------------------------+
```

Now, the following DDL statement is executed in the upstream to alter the table schema (namely, alter DECIMAL(11, 3) of c2 into DECIMAL(10, 3)):

```sql
ALTER TABLE db1.tbl1 CHANGE c2 c2 DECIMAL (10, 3);
```

Because this DDL statement is not supported by TiDB, the migration task of DM gets interrupted. Execute the `query-status <task-name>` command, and you can see the following error:

```
ERROR 8200 (HY000): Unsupported modify column: can't change decimal column precision
```

Assume that it is acceptable in the actual production environment that this DDL statement is not executed in the downstream TiDB (namely, the original table schema is retained). Then you can use `binlog skip <task-name>` to skip this DDL statement to resume the migration. The procedures are as follows:

1. Execute `binlog skip <task-name>` to skip the currently failed DDL statement:

    ```bash
    » binlog skip test
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

2. Execute `query-status <task-name>` to view the task status:

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

    You can see that the task runs normally and the wrong DDL is skipped.
