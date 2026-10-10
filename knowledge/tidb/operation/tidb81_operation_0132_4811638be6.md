# Switch DM-worker upstream MySQL connection procedures

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/usage-scenario-master-slave-switch.md`
- Source Title: `Switch DM-worker Connection between Upstream MySQL Instances`
- Source Heading Path: `Switch DM-worker Connection between Upstream MySQL Instances | Switch DM-worker Connection between Upstream MySQL Instances > Switch DM-worker connection via virtual IP | Switch DM-worker Connection between Upstream MySQL Instances > Change the address of the upstream MySQL instance that DM-worker connects to`
- Source Line Ranges: `5-52`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `mysql`, `upstream-switch`, `gtid`, `vip`, `source-configuration`, `pause-task`, `resume-task`, `stop-task`, `start-task`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0132_4811638be6`
- Source ID: `tidb-docs-8.1:dm/usage-scenario-master-slave-switch.md#switch-dm-worker-connection-between-upstream-mysql-instances`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc8ea63a3fc5051ebb6ebb16d4ae742a703c97d2ccee94dc749d280b578f73dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/usage-scenario-master-slave-switch#switch-dm-worker-connection-between-upstream-mysql-instances
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/usage-scenario-master-slave-switch.md

## Retrieval Guidance

- Use When: Use this chunk when handling a DM-worker upstream MySQL switch within the same primary-secondary migration cluster and you need the GTID-based procedures for switching via VIP or by changing the source configuration address.
- Retrieval Keywords: DM-worker connection switch, upstream MySQL instance, same primary-secondary migration cluster, enable-gtid: true, GTID sets mode, query-status, syncerBinlogGtid, SELECT @@GLOBAL.gtid_purged;, SELECT @@GLOBAL.gtid_executed;, gtid-S contains gtid-P, gtid-E contains gtid-S, switch via virtual IP, VIP, pause-task, resume-task, change upstream address, stop-task, operate-source stop, operate-source create, source configuration file, binlog required by DM-worker
- Follow-up Guidance: The source also distinguishes two exact procedures: switching DM-worker connection via virtual IP and changing the address of the upstream MySQL instance that DM-worker connects to.
- Classification Note: This is classified as an operation chunk because the content provides step-by-step procedures and command sequences for switching a DM-worker upstream MySQL connection under specific GTID conditions.

## Official Source Content

# Switch DM-worker Connection between Upstream MySQL Instances

When the upstream MySQL instance that DM-worker connects to needs downtime maintenance or when the instance crashes unexpectedly, you need to switch the DM-worker connection to another MySQL instance within the same migration group.

> **Note:**
>
> - You can switch the DM-worker connection to only an instance within the same primary-secondary migration cluster.
> - The MySQL instance to be newly connected to must have the binlog required by DM-worker.
> - DM-worker must operate in the GTID sets mode, which means you must specify `enable-gtid: true` in the corresponding source configuration file.
> - The connection switch only supports the following two scenarios. Strictly follow the procedures for each scenario. Otherwise, you might have to re-deploy the DM cluster according to the newly connected MySQL instance and perform the data migration task all over again.

For more details on GTID set, refer to [MySQL documentation](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-concepts.html#replication-gtids-concepts-gtid-sets).
## Switch DM-worker connection via virtual IP

When DM-worker connects the upstream MySQL instance via a virtual IP (VIP), switching the VIP connection to another MySQL instance means switching the MySQL instance connected to DM-worker, without the upstream connection address changed.

> **Note:**
>
> Make necessary changes to DM in this scenario. Otherwise, when you switch the VIP connection to another MySQL instance, DM might connect to the new and old MySQL instances at the same time in different connections. In this situation, the binlog replicated to DM is not consistent with other upstream status that DM receives, causing unpredictable anomalies and even data damage.

To switch one upstream MySQL instance (when DM-worker connects to it via a VIP) to another, perform the following steps:

1. Use the `query-status` command to get the GTID sets (`syncerBinlogGtid`) corresponding to the binlog that the current processing unit of binlog replication has replicated to the downstream. Mark the sets as `gtid-S`.
2. Use the `SELECT @@GLOBAL.gtid_purged;` command on the new MySQL instance to get the GTID sets corresponding to the purged binlogs. Mark the sets as `gtid-P`.
3. Use the `SELECT @@GLOBAL.gtid_executed;` command on the new MySQL instance to get the GTID sets corresponding to all successfully executed transactions. Mark the sets as `gtid-E`.
4. Make sure that the following conditions are met. Otherwise, you cannot switch the DM-work connection to the new MySQL instance:
    - `gtid-S` contains `gtid-P`. `gtid-P` can be empty.
    - `gtid-E` contains `gtid-S`.
5. Use `pause-task` to pause all running tasks of data migration.
6. Change the VIP for it to direct at the new MySQL instance.
7. Use `resume-task` to resume the previous migration task.
## Change the address of the upstream MySQL instance that DM-worker connects to

To make DM-worker connect to a new MySQL instance in the upstream by modifying the DM-worker configuration, perform the following steps:

1. Use the `query-status` command to get the GTID sets (`syncerBinlogGtid`) corresponding to the binlog that the current processing unit of binlog replication has replicated to the downstream. Mark this sets as `gtid-S`.
2. Use the `SELECT @@GLOBAL.gtid_purged;` command on the new MySQL instance to get the GTID sets corresponding to the purged binlogs. Mark this sets as `gtid-P`.
3. Use the `SELECT @@GLOBAL.gtid_executed;` command on the new MySQL instance to get the GTID sets corresponding to all successfully executed transactions. Mark this sets as `gtid-E`.
4. Make sure that the following conditions are met. Otherwise, you cannot switch the DM-work connection to the new MySQL instance:
    - `gtid-S` contains `gtid-P`. `gtid-P` can be empty.
    - `gtid-E` contains `gtid-S`.
5. Use `stop-task` to stop all running tasks of data migration.
6. Use the `operator-source stop` command to remove the source configuration corresponding to the address of the old MySQL instance from the DM cluster.
7. Update the address of the MySQL instance in the source configuration file and use the `operate-source create` command to reload the new source configuration in the DM cluster.
8. Use `start-task` to restart the migration task.
