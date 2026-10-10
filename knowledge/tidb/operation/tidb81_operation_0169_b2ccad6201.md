# DM task status, monitoring, logs, and related references

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step 3. (Optional) Use DM to perform incremental replication > Check the migration status | Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step 3. (Optional) Use DM to perform incremental replication > Monitor tasks and view logs | Migrate and Merge MySQL Shards of Large Datasets to TiDB > See also`
- Source Line Ranges: `369-406`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `dashboard`, `tiup`
- Topic Tags: `query-status`, `monitoring`, `grafana`, `logs`, `dm-master`, `dm-worker`, `task-history`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0169_b2ccad6201`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-shards-to-tidb.md#check-the-migration-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df56fd3fa77209334cb1c52cff47fb801fa3174d4025c5f2ee2383cf07c37e55`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb#check-the-migration-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need to check DM migration task status, find monitoring views in Grafana, or locate DM-master and DM-worker logs for migration tasks.
- Retrieval Keywords: query-status, tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}, Grafana, DM dashboard, Prometheus, Alertmanager, DM-master, DM-worker, dmctl output logs, --log-file, /dm-deploy/dm-master-8261/log/, /dm-deploy/dm-worker-8262/log/, Query Status, Monitor tasks and view logs
- Follow-up Guidance: The content also lists related references including Pause a Data Migration Task, Resume a Data Migration Task, Stop a Data Migration Task, Export and Import Data Sources and Task Configuration of Clusters, Handle Failed DDL Statements, and Handle Errors.
- Classification Note: This is classified as operation because the content focuses on observing running tasks, viewing monitoring metrics, and checking component logs rather than defining task configuration.

## Official Source Content

### Check the migration status

You can check if there are running migration tasks in the DM cluster and their status by running the `query-status` command in `tiup dmctl`.

```shell
tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}
```

For more information, see [Query Status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).
### Monitor tasks and view logs

You can view the history of a migration task and internal operational metrics through Grafana or logs.

- Via Grafana

    If Prometheus, Alertmanager, and Grafana are correctly deployed when you deploy the DM cluster using TiUP, you can view DM monitoring metrics in Grafana. Specifically, enter the IP address and port specified during deployment in Grafana and select the DM dashboard.

- Via logs

    When DM is running, DM-master, DM-worker, and dmctl output logs, which includes information about migration tasks. The log directory of each component is as follows.

    - DM-master log directory: It is specified by the DM-master command line parameter `--log-file`. If DM is deployed using TiUP, the log directory is `/dm-deploy/dm-master-8261/log/`.
    - DM-worker log directory: It is specified by the DM-worker command line parameter `--log-file`. If DM is deployed using TiUP, the log directory is `/dm-deploy/dm-worker-8262/log/`.
## See also

- [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview)
- [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview)
- [Pessimistic mode and optimistic mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge)
- [Pause a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-pause-task)
- [Resume a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-resume-task)
- [Stop a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-stop-task)
- [Export and Import Data Sources and Task Configuration of Clusters](https://docs.pingcap.com/tidb/stable/dm/dm-export-import-config)
- [Handle Failed DDL Statements](https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements)
- [Handle Errors](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling)
