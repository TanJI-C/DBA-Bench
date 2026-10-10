# Relay log overview and usage scenarios

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/relay-log.md`
- Source Title: `Data Migration Relay Log`
- Source Heading Path: `Data Migration Relay Log | Data Migration Relay Log > User scenarios | Data Migration Relay Log > Use relay log`
- Source Line Ranges: `5-31`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `relay-log`, `binlog`, `storage-directory`, `user-scenarios`, `migration-latency`, `upstream-load`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0029_a3b0f1f5fe`
- Source ID: `tidb-docs-8.1:dm/relay-log.md#data-migration-relay-log`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fb9e09b58e166fc037c54a8414cc8a4c71089d24b710aefd3f503fcc78b986f2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/relay-log#data-migration-relay-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/relay-log.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks what DM relay log is, where relay logs are stored locally, or when enabling relay log helps with upstream binlog purge risk, upstream connection pressure, or incremental migration after a long full migration.
- Retrieval Keywords: Data Migration Relay Log, relay log, numbered files, index file, upstream binlog, local configuration directory, <deploy_dir>/<relay_log>, relay-dir, DM-worker, task-mode=all, full and incremental data migration, binlog purged, relieves the pressure on the upstream database, latency-sensitive
- Follow-up Guidance: The source continues with how to enable and disable relay log, query relay log status, and purge relay log.
- Classification Note: This is classified as architecture because the content explains what relay log consists of, where DM-worker stores it, and the operational scenarios and tradeoffs for using it.

## Official Source Content

# Data Migration Relay Log

The Data Migration (DM) relay log consists of several sets of numbered files containing events that describe database changes, and an index file that contains the names of all used relay log files.

After relay log is enabled, DM-worker automatically migrates the upstream binlog to the local configuration directory (the default migration directory is `<deploy_dir>/<relay_log>` if DM is deployed using TiUP). The default value of `<relay_log>` is `relay-dir` and can be modified in [Upstream Database Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file). Since v5.4.0, you can configure the local configuration directory through `relay-dir` in the [DM-worker configuration file](https://docs.pingcap.com/tidb/stable/dm/dm-worker-configuration-file), which takes precedence over the configuration file of the upstream database.
## User scenarios

In MySQL, storage space is limited, so the binlog is automatically purged when the maximum retention time is reached. After the upstream database purges the binlog, DM fails to pull the purged binlog and the migration task fails. For each migration task, DM creates a connection in the upstream to pull binlog. Too many connections might cause a heavy workload on the upstream database.

When the relay log is enabled, multiple migration task with the same upstream database can reuse the relay log that has been pulled to the local disk. This **relieves the pressure on the upstream database**.

For full and incremental data migration tasks (`task-mode=all`), DM needs to first migrate full data and then perform incremental migration based on binlog. If the full migration phase takes long, the upstream binlog might be purged, which results in incremental migration failure. To avoid this situation, you can enable the relay log feature so that DM automatically retains enough log in the local disk and **ensures the incremental migration task can be performed normally**.

It is generally recommended to enable relay log, but be aware of the following potential issue:

Because relay log must be written to the disk, it consumes external IO and CPU resources. This prolongs the whole data replication process and increases the data replication latency. For **latency-sensitive** scenarios, it is not recommended to enable relay log.

> **Note:**
>
> In DM v2.0.7 and later versions, relay log writes are optimized. The latency and CPU resource consumption is relatively low.
## Use relay log

This section describes how to enable and disable relay log, query relay log status, and purge relay log.
