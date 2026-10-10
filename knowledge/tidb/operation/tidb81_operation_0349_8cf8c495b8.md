# Create, start, and verify DM incremental replication task

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-sql-shards.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform incremental data replication from MySQL to TiDB Cloud > Step 2. Create a replication task | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform incremental data replication from MySQL to TiDB Cloud > Step 3. Start the replication task | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform incremental data replication from MySQL to TiDB Cloud > Step 4. Check the replication task status`
- Source Line Ranges: `340-603`
- Source Scope: `cloud`
- Primary Component: `dm`
- Related Components: `cloud`, `dumpling`, `tidb`, `tiup`
- Topic Tags: `incremental-replication`, `task-configuration`, `binlog-position`, `gtid`, `precheck`, `task-start`, `status-check`, `shard-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0349_8cf8c495b8`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-sql-shards.md#step-2-create-a-replication-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b46dcc03292391761d549067e35c4f6224a4ed77e9c6b7f19d29990d2154c6e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-sql-shards#step-2-create-a-replication-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-sql-shards.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented DM workflow to create an incremental replication task for MySQL shards to TiDB Cloud, set each source meta starting point from Dumpling metadata, run precheck, start the task, and verify status.
- Retrieval Keywords: test-task1.yaml, task-mode: incremental, shard-mode: "pessimistic", meta.binlog-name, meta.binlog-pos, meta.binlog-gtid, Dumpling metadata file, SHOW MASTER STATUS, safe-mode, mysql-replica-01, mysql-replica-02, tiup dmctl check-task dm-task.yaml, tiup dmctl start-task dm-task.yaml, tiup dmctl query-status test-task1, ignore-checking-items, block-allow-list, route-rules, filter-rules, secondsBehindMaster, stage: "Running", unit: "Sync"
- Follow-up Guidance: The source also points to DM Task Configurations for detailed task options, DM error handling and DM FAQ for start failures, and Query Status for interpreting the status output.
- Classification Note: This is classified as an operation chunk because the content provides step-by-step DM commands and task configuration examples for creating, starting, prechecking, and checking an incremental replication task.

## Official Source Content

### Step 2. Create a replication task

1. Create a `test-task1.yaml` file for the replication task.

2. Find the starting point in the metadata file of MySQL instance1 exported by Dumpling. For example:

    ```toml
    Started dump at: 2022-05-25 10:16:26
    SHOW MASTER STATUS:
           Log: mysql-bin.000002
           Pos: 246546174
           GTID:b631bcad-bb10-11ec-9eee-fec83cf2b903:1-194801
    Finished dump at: 2022-05-25 10:16:27
    ```

3. Find the starting point in the metadata file of MySQL instance2 exported by Dumpling. For example:

    ```toml
    Started dump at: 2022-05-25 10:20:32
    SHOW MASTER STATUS:
           Log: mysql-bin.000001
           Pos: 1312659
           GTID:cd21245e-bb10-11ec-ae16-fec83cf2b903:1-4036
    Finished dump at: 2022-05-25 10:20:32
    ```

4. Edit the task configuration file `test-task1`, to configure the incremental replication mode and replication starting point for each data source.

    ```yaml
    ## ********* Task Configuration *********
    name: test-task1
    shard-mode: "pessimistic"
    # Task mode. The "incremental" mode only performs incremental data migration.
    task-mode: incremental
    # timezone: "UTC"

    ## ******** Data Source Configuration **********
    ## (Optional) If you need to incrementally replicate data that has already been migrated in the full data migration, you need to enable the safe mode to avoid the incremental data migration error.
    ##  This scenario is common in the following case: the full migration data does not belong to the data source's consistency snapshot, and after that, DM starts to replicate incremental data from a position earlier than the full migration.
    syncers:           # The running configurations of the sync processing unit.
     global:           # Configuration name.
       safe-mode: false # # If this field is set to true, DM changes INSERT of the data source to REPLACE for the target database,
                        # # and changes UPDATE of the data source to DELETE and REPLACE for the target database.
                        # # This is to ensure that when the table schema contains a primary key or unique index, DML statements can be imported repeatedly.
                        # # In the first minute of starting or resuming an incremental migration task, DM automatically enables the safe mode.
    mysql-instances:
    - source-id: "mysql-replica-01"
       block-allow-list:  "bw-rule-1"
       route-rules: ["store-route-rule", "sale-route-rule"]
       filter-rules: ["store-filter-rule", "sale-filter-rule"]
       syncer-config-name: "global"
       meta:
         binlog-name: "mysql-bin.000002"
         binlog-pos: 246546174
         binlog-gtid: "b631bcad-bb10-11ec-9eee-fec83cf2b903:1-194801"
    - source-id: "mysql-replica-02"
       block-allow-list:  "bw-rule-1"
       route-rules: ["store-route-rule", "sale-route-rule"]
       filter-rules: ["store-filter-rule", "sale-filter-rule"]
       syncer-config-name: "global"
       meta:
         binlog-name: "mysql-bin.000001"
         binlog-pos: 1312659
         binlog-gtid: "cd21245e-bb10-11ec-ae16-fec83cf2b903:1-4036"

    ## ******** Configuration of the target TiDB cluster on TiDB Cloud **********
    target-database:       # The target TiDB cluster on TiDB Cloud
     host: "tidb.xxxxxxx.xxxxxxxxx.ap-northeast-1.prod.aws.tidbcloud.com"
     port: 4000
     user: "root"
     password: "${password}"  # If the password is not empty, it is recommended to use a dmctl-encrypted cipher.

    ## ******** Function Configuration **********
    routes:
     store-route-rule:
       schema-pattern: "store_*"
       target-schema: "store"
     sale-route-rule:
       schema-pattern: "store_*"
       table-pattern: "sale_*"
       target-schema: "store"
       target-table:  "sales"
    filters:
     sale-filter-rule:
       schema-pattern: "store_*"
       table-pattern: "sale_*"
       events: ["truncate table", "drop table", "delete"]
       action: Ignore
     store-filter-rule:
       schema-pattern: "store_*"
       events: ["drop database"]
       action: Ignore
    block-allow-list:
     bw-rule-1:
       do-dbs: ["store_*"]

    ## ******** Ignore check items **********
    ignore-checking-items: ["table_schema","auto_increment_ID"]
    ```

For detailed task configurations, see [DM Task Configurations](https://docs.pingcap.com/tidb/stable/task-configuration-file-full).

To run a data replication task smoothly, DM triggers a precheck automatically at the start of the task and returns the check results. DM starts the replication only after the precheck is passed. To trigger a precheck manually, run the check-task command:

```shell
[root@localhost ~]# tiup dmctl --master-addr 192.168.11.110:9261 check-task dm-task.yaml
```

The following is an example output:

```shell
tiup is checking updates for component dmctl ...

Starting component `dmctl`: /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl --master-addr 192.168.11.110:9261 check-task dm-task.yaml

{
   "result": true,
   "msg": "check pass!!!"
}
```
### Step 3. Start the replication task

Use `tiup dmctl` to run the following command to start the data replication task:

```shell
[root@localhost ~]# tiup dmctl --master-addr ${advertise-addr}  start-task dm-task.yaml
```

The parameters used in the command above are described as follows:

|Parameter              |Description    |
|-                      |-              |
|`--master-addr`        |The `{advertise-addr}` of any DM-master node in the cluster where `dmctl` is to be connected. For example: 192.168.11.110:9261|
|`start-task`           |Starts the migration task.|

The following is an example output:

```shell
tiup is checking updates for component dmctl ...

Starting component `dmctl`: /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl --master-addr 192.168.11.110:9261 start-task dm-task.yaml

{
   "result": true,
   "msg": "",
   "sources": [
       {
           "result": true,
           "msg": "",
           "source": "mysql-replica-01",
           "worker": "dm-192.168.11.111-9262"
       },

       {
           "result": true,
           "msg": "",
           "source": "mysql-replica-02",
           "worker": "dm-192.168.11.112-9262"
       }
   ],
   "checkResult": ""
}
```

If the task fails to start, check the prompt message and fix the configuration. After that, you can re-run the command above to start the task.

If you encounter any problem, refer to [DM error handling](https://docs.pingcap.com/tidb/stable/dm-error-handling) and [DM FAQ](https://docs.pingcap.com/tidb/stable/dm-faq).
### Step 4. Check the replication task status

To learn whether the DM cluster has an ongoing replication task and view the task status, run the `query-status` command using `tiup dmctl`:

```shell
[root@localhost ~]# tiup dmctl --master-addr 192.168.11.110:9261 query-status test-task1
```

The following is an example output:

```shell
{
   "result": true,
   "msg": "",
   "sources": [
       {
           "result": true,
           "msg": "",
           "sourceStatus": {
               "source": "mysql-replica-01",
               "worker": "dm-192.168.11.111-9262",
               "result": null,
               "relayStatus": null
           },

           "subTaskStatus": [
               {
                   "name": "test-task1",
                   "stage": "Running",
                   "unit": "Sync",
                   "result": null,
                   "unresolvedDDLLockID": "",
                   "sync": {
                       "totalEvents": "4048",
                       "totalTps": "3",
                       "recentTps": "3",
                       "masterBinlog": "(mysql-bin.000002, 246550002)",
                       "masterBinlogGtid": "b631bcad-bb10-11ec-9eee-fec83cf2b903:1-194813",
                       "syncerBinlog": "(mysql-bin.000002, 246550002)",
                       "syncerBinlogGtid": "b631bcad-bb10-11ec-9eee-fec83cf2b903:1-194813",
                       "blockingDDLs": [
                       ],
                       "unresolvedGroups": [
                       ],
                       "synced": true,
                       "binlogType": "remote",
                       "secondsBehindMaster": "0",
                       "blockDDLOwner": "",
                       "conflictMsg": ""
                   }
               }
           ]
       },
       {
           "result": true,
           "msg": "",
           "sourceStatus": {
               "source": "mysql-replica-02",
               "worker": "dm-192.168.11.112-9262",
               "result": null,
               "relayStatus": null
           },
           "subTaskStatus": [
               {
                   "name": "test-task1",
                   "stage": "Running",
                   "unit": "Sync",
                   "result": null,
                   "unresolvedDDLLockID": "",
                   "sync": {
                       "totalEvents": "33",
                       "totalTps": "0",
                       "recentTps": "0",
                       "masterBinlog": "(mysql-bin.000001, 1316487)",
                       "masterBinlogGtid": "cd21245e-bb10-11ec-ae16-fec83cf2b903:1-4048",
                       "syncerBinlog": "(mysql-bin.000001, 1316487)",
                       "syncerBinlogGtid": "cd21245e-bb10-11ec-ae16-fec83cf2b903:1-4048",
                       "blockingDDLs": [
                       ],
                       "unresolvedGroups": [
                       ],
                       "synced": true,
                       "binlogType": "remote",
                       "secondsBehindMaster": "0",
                       "blockDDLOwner": "",
                       "conflictMsg": ""
                   }
               }
           ]
       }
   ]
}
```

For a detailed interpretation of the results, see [Query Status](https://docs.pingcap.com/tidb/stable/dm-query-status).
