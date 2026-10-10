# Create the sharded migration task and verify consistency

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/quick-start-create-task.md`
- Source Title: `Create a Data Migration Task`
- Source Heading Path: `Create a Data Migration Task > Create a data migration task | Create a Data Migration Task > Verify data`
- Source Line Ranges: `148-232`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `ecosystem`
- Topic Tags: `task-configuration`, `shard-merge`, `routing-rules`, `block-allow-list`, `start-task`, `data-validation`, `sync-diff-inspector`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0015_7ac15c67a9`
- Source ID: `tidb-docs-8.1:dm/quick-start-create-task.md#create-a-data-migration-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `619f2d3f0d8d139dbcdc5e5312a9a6e5fae5928fbfc0297e7d5d26641d32b456`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/quick-start-create-task#create-a-data-migration-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/quick-start-create-task.md

## Retrieval Guidance

- Use When: Use this chunk when you need the example DM task configuration for migrating sharded MySQL tables into db_target.t_target, starting the task with dmctl, and checking consistency with sync-diff-inspector.
- Retrieval Keywords: Create a data migration task, Verify data, conf/task.yaml, start-task, ./dmctl --master-addr 127.0.0.1:8261 start-task conf/task.yaml, name: test, task-mode: all, shard-mode: pessimistic, target-database, mysql-instances, block-allow-list, black-white-list, route-rules, sharding-route-rules-table, sharding-route-rules-schema, db_target, t_target, do-dbs, do-tables, sync-diff-inspector, shard-diff
- Follow-up Guidance: The chunk says you can modify upstream MySQL sharded-table data and then use sync-diff-inspector to check whether upstream and downstream data are consistent.
- Classification Note: This is classified as data_pipeline because the content provides the sharded migration task definition, source-to-target routing rules, task startup command, and post-migration data verification context.

## Official Source Content

## Create a data migration task

After importing [prepared data](#prepare-data), there are several sharded tables on both MySQL1 and MySQL2 instances. These tables have identical structure and the same prefix "t" in the table names; the databases where these tables are located are all prefixed with "sharding"; and there is no conflict between the primary keys or the unique keys (in each sharded table, the primary keys or the unique keys are different from those of other tables).

Now, suppose that you need to migrate these sharded tables to the `db_target.t_target` table in TiDB. The steps are as follows.

1. Create the configuration file of the task:

    ```yaml
    ---
    name: test
    task-mode: all
    shard-mode: "pessimistic"
    target-database:
      host: "127.0.0.1"
      port: 4000
      user: "root"
      password: "" # It is recommended to use password encrypted with dmctl if the password is not empty.

    mysql-instances:
      - source-id: "mysql-replica-01"
        block-allow-list:  "instance"  # This configuration applies to DM versions higher than v2.0.0-beta.2. Use black-white-list otherwise.
        route-rules: ["sharding-route-rules-table", "sharding-route-rules-schema"]
        mydumper-thread: 4
        loader-thread: 16
        syncer-thread: 16
      - source-id: "mysql-replica-02"
        block-allow-list:  "instance"  # This configuration applies to DM versions higher than v2.0.0-beta.2. Use black-white-list otherwise.
        route-rules: ["sharding-route-rules-table", "sharding-route-rules-schema"]
        mydumper-thread: 4
        loader-thread: 16
        syncer-thread: 16
    block-allow-list:  # This configuration applies to DM versions higher than v2.0.0-beta.2. Use black-white-list otherwise.
      instance:
        do-dbs: ["~^sharding[\\d]+"]
        do-tables:
        - db-name: "~^sharding[\\d]+"
          tbl-name: "~^t[\\d]+"
    routes:
      sharding-route-rules-table:
        schema-pattern: sharding*
        table-pattern: t*
        target-schema: db_target
        target-table: t_target
      sharding-route-rules-schema:
        schema-pattern: sharding*
        target-schema: db_target
    ```

2. To create a task using dmctl, write the above configurations to the `conf/task.yaml` file:

    ```bash
    ./dmctl --master-addr 127.0.0.1:8261 start-task conf/task.yaml
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
            },
            {
                "result": true,
                "msg": "",
                "source": "mysql-replica-02",
                "worker": "worker2"
            }
        ]
    }
    ```

Now, you have successfully created a task to migrate the sharded tables from the MySQL1 and MySQL2 instances to TiDB.
## Verify data

You can modify data in the upstream MySQL sharded tables. Then use [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/shard-diff) to check whether the upstream and downstream data are consistent. Consistent data means that the migration task works well, which also indicates that the cluster works well.
