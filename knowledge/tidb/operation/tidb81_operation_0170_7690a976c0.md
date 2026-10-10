# Start and verify a DM migration task

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-small-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Small Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Small Datasets to TiDB > Step 3. Start the task | Migrate and Merge MySQL Shards of Small Datasets to TiDB > Step 4. Check the task`
- Source Line Ranges: `188-224`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `task-start`, `precheck`, `dmctl`, `query-status`, `error-handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0170_7690a976c0`
- Source ID: `tidb-docs-8.1:migrate-small-mysql-shards-to-tidb.md#step-3-start-the-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9eb0b6f8ec0168f381405706b51369771b58a6830c08e1142c15907a6d19fe58`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb#step-3-start-the-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-small-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this content when looking for the DM commands to precheck, start, and verify a migration task and how to inspect task status after startup.
- Retrieval Keywords: tiup dmctl check-task task.yaml, tiup dmctl start-task task.yaml, tiup dmctl --master-addr ${advertise-addr}, query-status ${task-name}, DM-master advertise-addr, migration task fails to start, Handle Errors, FAQ, TiDB Data Migration Query Status
- Follow-up Guidance: If the migration task fails to start, modify the configuration information according to the error information and run `start-task task.yaml` again, and `query-status ${task-name}` can be used to view more detailed information when errors occur.
- Classification Note: This is classified as an operation chunk because the official content gives procedural `tiup dmctl` commands for `check-task`, `start-task`, and `query-status` when managing a DM migration task.

## Official Source Content

## Step 3. Start the task

Before starting a migration task, run the `check-task` subcommand in `tiup dmctl` to check whether the configuration meets the requirements of DM so as to avoid possible errors.

```shell
tiup dmctl --master-addr ${advertise-addr} check-task task.yaml
```

Run the following command in `tiup dmctl` to start a migration task:

```shell
tiup dmctl --master-addr ${advertise-addr} start-task task.yaml
```

| Parameter | Description|
|-|-|
|`--master-addr`| `{advertise-addr}` of any DM-master node in the cluster that dmctl connects to. For example: 172.16.10.71:8261 |
|`start-task`   | Starts the data migration task. |

If the migration task fails to start, modify the configuration information according to the error information, and then run `start-task task.yaml` again to start the migration task. If you encounter problems, see [Handle Errors](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling) and [FAQ](https://docs.pingcap.com/tidb/stable/dm/dm-faq).
## Step 4. Check the task

After starting the migration task, you can use `dmtcl tiup` to run `query-status` to view the status of the task.

```shell
tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}
```

If you encounter errors, use `query-status ${task-name}` to view more detailed information. For details about the query results, task status and sub task status of the `query-status` command, see [TiDB Data Migration Query Status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).
