# DM restart failures, binlog purge recovery, and Grafana dashboard issue

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-faq.md`
- Source Title: `TiDB Data Migration FAQs`
- Source Heading Path: `TiDB Data Migration FAQs > In DM v2.0, why does the full import task fail if DM restarts during the task? | TiDB Data Migration FAQs > Why does DM report the error `ERROR 1236 (HY000): The slave is connecting using CHANGE MASTER TO MASTER_AUTO_POSITION = 1, but the master has purged binary logs containing GTIDs that the slave requires.` if it restarts during an incremental task? | TiDB Data Migration FAQs > Why does the Grafana dashboard of a DM cluster display `failed to fetch dashboard` if the cluster is deployed using TiUP v1.3.0 or v1.3.1?`
- Source Line Ranges: `202-249`
- Source Scope: `shared`
- Primary Component: `dm`
- Related Components: `lightning`, `dumpling`, `tiup`
- Topic Tags: `full-import`, `restart-failure`, `worker-binding`, `remove-meta`, `incremental-mode`, `gtid`, `binlog-purge`, `relay-log`, `grafana`, `dashboard-fetch`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0016_03ae95eec2`
- Source ID: `tidb-docs-8.1:dm/dm-faq.md#in-dm-v2-0-why-does-the-full-import-task-fail-if-dm-restarts-during-the-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `faaf1d2f3b2693f9fe8b49fd39e372e5e5d2b3cc8c5ee14588b832a2be896afb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-faq#in-dm-v2-0-why-does-the-full-import-task-fail-if-dm-restarts-during-the-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-faq.md

## Retrieval Guidance

- Use When: Use this chunk when recovering from DM restart-related failures during full import or incremental replication, or when a DM Grafana dashboard shows `failed to fetch dashboard` on clusters deployed with TiUP v1.3.0 or v1.3.1.
- Retrieval Keywords: DM v2.0 full import fail if DM restarts, start-task --remove-meta, full import restart failure, upstream data sources and DM-worker bindings, TiDB-Lightning, Local-backend mode, task-mode incremental, mysql-instance.meta.pos, ERROR 1236 (HY000), MASTER_AUTO_POSITION = 1, master has purged binary logs containing GTIDs that the slave requires, expire_logs_days, relay log feature, failed to fetch dashboard, TiUP v1.3.0, TiUP v1.3.1, TiUP v1.3.2, tiup update --self && tiup update dm, tiup dm restart $cluster_name -R grafana, deploy/grafana-$port/bin/public, TiUP DM offline package
- Follow-up Guidance: The content provides recovery paths such as deleting migrated or imported downstream data, restarting a task with `--remove-meta`, switching to `incremental` with `mysql-instance.meta.pos`, enabling relay logs, or upgrading TiUP and restarting Grafana.
- Classification Note: This chunk is classified as recovery because the official content gives specific remediation procedures for restart-induced migration failures, purged binlog recovery, and restoring a broken Grafana dashboard.

## Official Source Content

## In DM v2.0, why does the full import task fail if DM restarts during the task?

In DM v2.0.1 and earlier versions, if DM restarts before the full import completes, the bindings between upstream data sources and DM-worker nodes might change. For example, it is possible that the intermediate data of the dump unit is on DM-worker node A but the load unit is run by DM-worker node B, thus causing the operation to fail.

The following are two solutions to this issue:

- If the data volume is small (less than 1 TB) or the task merges sharded tables, take these steps:

    1. Clean up the imported data in the downstream database.
    2. Remove all files in the directory of exported data.
    3. Delete the task using dmctl and run the command `start-task --remove-meta` to create a new task.

    After the new task starts, it is recommended to ensure that there is no redundant DM worker node and avoid restarting or upgrading the DM cluster during the full import.

- If the data volume is large (more than 1 TB), take these steps:

    1. Clean up the imported data in the downstream database.
    2. Deploy TiDB-Lightning to the DM worker nodes that process the data.
    3. Use the Local-backend mode of TiDB-Lightning to import data that DM dump units export.
    4. After the full import completes, edit the task configuration file in the following ways and restart the task:
        - Change `task-mode` to `incremental`.
        - Set the value of `mysql-instance.meta.pos` to the position recorded in the metadata file that the dump unit outputs.
## Why does DM report the error `ERROR 1236 (HY000): The slave is connecting using CHANGE MASTER TO MASTER_AUTO_POSITION = 1, but the master has purged binary logs containing GTIDs that the slave requires.` if it restarts during an incremental task?

This error indicates that the upstream binlog position recorded in the metadata file output by the dump unit has been purged during the full migration.

If this issue occurs, you need to pause the task, delete all migrated data in the downstream database, and start a new task with the `--remove-meta` option.

You can avoid this issue in advance by configuring in the following ways:

1. Increase the value of `expire_logs_days` in the upstream MySQL database to avoid wrongly purging needed binlog files before the full migration task completes. If the data volume is large, it is recommended to use dumpling and TiDB-Lightning at the same time to speed up the task.
2. Enable the relay log feature for this task so that DM can read data from relay logs even though the binlog position is purged.
## Why does the Grafana dashboard of a DM cluster display `failed to fetch dashboard` if the cluster is deployed using TiUP v1.3.0 or v1.3.1?

This is a known bug of TiUP, which is fixed in TiUP v1.3.2. The following are two solutions to this issue:

- Solution one:
    1. Upgrade TiUP to a later version using the command `tiup update --self && tiup update dm`.
    2. Scale in and then scale out Grafana nodes in the cluster to restart the Grafana service.
- Solution two:
    1. Back up the `deploy/grafana-$port/bin/public` folder.
    2. Download the [TiUP DM offline package](https://download.pingcap.com/tidb-dm-v2.0.1-linux-amd64.tar.gz) and unpack it.
    3. Unpack the `grafana-v4.0.3-**.tar.gz` in the offline package.
    4. Replace the folder `deploy/grafana-$port/bin/public` with the `public` folder in `grafana-v4.0.3-**.tar.gz`.
    5. Execute `tiup dm restart $cluster_name -R grafana` to restart the Grafana service.
