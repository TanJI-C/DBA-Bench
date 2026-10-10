# BR FAQ overview, flashback recovery, and backup auto-tune slowdown

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/backup-and-restore-faq.md`
- Source Title: `Backup & Restore FAQs`
- Source Heading Path: `Backup & Restore FAQs | Backup & Restore FAQs > What should I do to quickly recover data after mistakenly deleting or updating data? | Backup & Restore FAQs > In TiDB v5.4.0 and later versions, when backup tasks are performed on the cluster under a heavy workload, why does the speed of backup tasks become slow?`
- Source Line Ranges: `5-28`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `sql`, `tikv`
- Topic Tags: `flashback`, `misoperation`, `backup`, `auto-tune`, `workload`, `threads`, `resource-limiting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0139_08dfdcc61c`
- Source ID: `tidb-docs-8.1:faq/backup-and-restore-faq.md#backup-restore-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c820c33e295abe4f2ec74bde33d9d0700cbf4ee40adf9a6636643d5746d9abcd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#backup-restore-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/backup-and-restore-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to recover from mistaken DELETE or UPDATE operations with flashback, or why BR backup throughput is lower on heavily loaded clusters after v5.4.0 because of auto-tune and thread limits.
- Retrieval Keywords: flashback feature, Flashback Cluster, Flashback Database, mistakenly deleting or updating data, GC time, backup auto-tune, heavy workload backup slow, backup.enable-auto-tune, backup.num-threads, tikv-ctl, dynamically configuring the auto-tune feature, TiDB v5.4.0, TiDB v6.4.0
- Follow-up Guidance: It also states that on an offline cluster you can increase `backup.num-threads` using `tikv-ctl`, and it points to the Backup Auto-Tune documentation and dynamic TiKV configuration.
- Classification Note: This is classified as operation because the content explains recovery and backup runtime behavior, including flashback usage and operational tuning of BR auto-tune and backup threads.

## Official Source Content

# Backup & Restore FAQs

This document lists the frequently asked questions (FAQs) and the solutions of TiDB Backup & Restore (BR).
## What should I do to quickly recover data after mistakenly deleting or updating data?

TiDB v6.4.0 introduces the flashback feature. You can use this feature to quickly recover data within the GC time to a specified point in time. Therefore, if misoperations occur, you can use this feature to recover data. For details, see [Flashback Cluster](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) and [Flashback Database](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-database).
## In TiDB v5.4.0 and later versions, when backup tasks are performed on the cluster under a heavy workload, why does the speed of backup tasks become slow?

Starting from TiDB v5.4.0, BR introduces the auto-tune feature for backup tasks. For clusters in v5.4.0 or later versions, this feature is enabled by default. When the cluster workload is heavy, the feature limits the resources used by backup tasks to reduce the impact on the online cluster. For more information, refer to [Backup Auto-Tune](https://docs.pingcap.com/tidb/stable/br/br-auto-tune).

TiKV supports [dynamically configuring](https://docs.pingcap.com/tidb/stable/tikv-control#modify-the-tikv-configuration-dynamically) the auto-tune feature. You can enable or disable the feature by the following methods without restarting your cluster:

- Disable auto-tune: Set the TiKV configuration item [`backup.enable-auto-tune`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-auto-tune-new-in-v540) to `false`.
- Enable auto-tune: Set `backup.enable-auto-tune` to `true`. For clusters upgraded from v5.3.x to v5.4.0 or later versions, the auto-tune feature is disabled by default. You need to manually enable it.

To use `tikv-ctl` to enable or disable auto-tune, refer to [Use auto-tune](https://docs.pingcap.com/tidb/stable/br/br-auto-tune#use-auto-tune).

In addition, auto-tune reduces the default number of threads used by backup tasks. For details, see `backup.num-threads`](/tikv-configuration-file.md#num-threads-1). Therefore, on the Grafana Dashboard, the speed, CPU usage, and I/O resource utilization used by backup tasks are lower than those of versions earlier than v5.4.0. Before v5.4.0, the default value of `backup.num-threads` was `CPU * 0.75`, that is, the number of threads used by backup tasks makes up 75% of the logical CPU cores. The maximum value of it was `32`. Starting from v5.4.0, the default value of this configuration item is `CPU * 0.5`, and its maximum value is `8`.

When you perform backup tasks on an offline cluster, to speed up the backup, you can modify the value of `backup.num-threads` to a larger number using `tikv-ctl`.
