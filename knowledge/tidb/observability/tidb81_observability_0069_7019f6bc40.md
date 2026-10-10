# Monitor DM tasks, inspect logs, and related references

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-small-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Small Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Small Datasets to TiDB > Step 5. Monitor tasks and check logs (optional) | Migrate and Merge MySQL Shards of Small Datasets to TiDB > See also`
- Source Line Ranges: `225-247`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `dashboard`, `tiup`, `shared`
- Topic Tags: `monitoring`, `grafana`, `logs`, `metrics`, `troubleshooting`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0069_7019f6bc40`
- Source ID: `tidb-docs-8.1:migrate-small-mysql-shards-to-tidb.md#step-5-monitor-tasks-and-check-logs-optional`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1f6f7599c86ae2d46790ce5665e5aa73055e3ce2c7f79e80c1c08ae8c43f6463`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb#step-5-monitor-tasks-and-check-logs-optional
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-small-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this content when looking for where to monitor DM migration task history and internal operational metrics or where DM component logs are stored.
- Retrieval Keywords: Grafana DM dashboard, Prometheus Alertmanager Grafana, DM monitoring metrics, DM-master log directory, DM-worker log directory, dmctl output logs, --log-file, /dm-deploy/dm-master-8261/log/, /dm-deploy/dm-worker-8262/log/, history of a migration task, internal operational metrics, Handle Performance Issues
- Follow-up Guidance: The source also points to related references including shard merge migration, Handle Errors, Handle Performance Issues, and FAQ.
- Classification Note: This is classified as an observability chunk because the official content focuses on viewing task history and metrics through Grafana and checking DM-master, DM-worker, and dmctl logs.

## Official Source Content

## Step 5. Monitor tasks and check logs (optional)

You can view the history of a migration task and internal operational metrics through Grafana or logs.

- Via Grafana

    If Prometheus, Alertmanager, and Grafana are correctly deployed when you deploy the DM cluster using TiUP, you can view DM monitoring metrics in Grafana. Specifically, enter the IP address and port specified during deployment in Grafana and select the DM dashboard.

- Via logs

    When DM is running, DM-master, DM-worker, and dmctl output logs, which includes information about migration tasks. The log directory of each component is as follows.

    - DM-master log directory: It is specified by the DM-master process parameter `--log-file`. If DM is deployed using TiUP, the log directory is `/dm-deploy/dm-master-8261/log/`.
    - DM-worker log directory: It is specified by the DM-worker process parameter `--log-file`. If DM is deployed using TiUP, the log directory is `/dm-deploy/dm-worker-8262/log/`.
## See also

- [Migrate and Merge MySQL Shards of Large Datasets to TiDB](https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb).
- [Merge and Migrate Data from Sharded Tables](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge)
- [Best Practices of Data Migration in the Shard Merge Scenario](https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices)
- [Handle Errors](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling)
- [Handle Performance Issues](https://docs.pingcap.com/tidb/stable/dm/dm-handle-performance-issues)
- [FAQ](https://docs.pingcap.com/tidb/stable/dm/dm-faq)
