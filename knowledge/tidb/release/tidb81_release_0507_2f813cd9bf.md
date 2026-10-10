# Reliability features: background task control, statistics locking, hash join control, stats cache quota

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `179-209`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `lightning`, `br`, `sql`
- Topic Tags: `reliability`, `resource-control`, `background-tasks`, `statistics`, `lock-statistics`, `hash-join`, `system-variables`, `memory-control`, `stats-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0507_2f813cd9bf`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#reliability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c5c4706f0d3b7cd967bcc2ffcee02cfc297fedec8c0c73328d2e9abf31806275`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#reliability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 reliability changes around background task control, lock statistics, hash join selection, or statistics cache memory quota.
- Retrieval Keywords: background tasks, default resource group, lightning, IMPORT INTO, br, backup and restore, PITR is not supported, ddl, stats, manage background tasks, lock statistics, unlock statistics, collect statistics, specific partitions, tidb_opt_enable_hash_join, hash joins for tables, optimizer_switch, ON, OFF, execution plan rollbacks, tidb_stats_cache_mem_quota, statistics cache, memory usage limit, evicts inactive cache entries
- Follow-up Guidance: The source points to documentation for managing background tasks, lock statistics, tidb_opt_enable_hash_join, and tidb_stats_cache_mem_quota.
- Classification Note: This is a release-note chunk for TiDB reliability features because it summarizes new or GA capabilities for task resource control, statistics stability, join-plan control, and statistics cache memory control in v7.4.0.

## Official Source Content

- `lightning`: perform import tasks using [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) or [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into).
    - `br`: perform backup and restore tasks using [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview). PITR is not supported.
    - `ddl`: control the resource usage during the batch data write back phase of Reorg DDLs.
    - `stats`: the [collect statistics](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics) tasks that are manually executed or automatically triggered by TiDB.

  By default, the task types that are marked as background tasks are empty, and the management of background tasks is disabled. This default behavior is the same as that of versions prior to TiDB v7.4.0. To manage background tasks, you need to manually modify the background task types of the `default` resource group.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-background-tasks).

* Lock statistics becomes generally available (GA) [#46351](https://github.com/pingcap/tidb/issues/46351) @[hi-rustin](https://github.com/Rustin170506)

    In v7.4.0, [lock statistics](https://docs.pingcap.com/tidb/stable/statistics#lock-statistics) becomes generally available. Now, to ensure operational security, locking and unlocking statistics require the same privileges as collecting statistics. In addition, TiDB supports locking and unlocking statistics for specific partitions, providing greater flexibility. If you are confident in queries and execution plans in the database and want to prevent any changes from occurring, you can lock statistics to enhance stability.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/statistics#lock-statistics).

* Introduce a system variable to control whether to select hash joins for tables [#46695](https://github.com/pingcap/tidb/issues/46695) @[coderplay](https://github.com/coderplay)

     MySQL 8.0 introduces hash joins for tables as a new feature. This feature is primarily used to join two relatively large tables and result sets. However, for transactional workloads, or some applications running on MySQL 5.7, hash joins for tables might pose a performance risk. MySQL provides the [`optimizer_switch`](https://dev.mysql.com/doc/refman/8.0/en/switchable-optimizations.html#optflag_block-nested-loop) to control whether to select hash joins at the global or session level.

    Starting from v7.4.0, TiDB introduces the system variable [`tidb_opt_enable_hash_join`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_hash_join-new-in-v656-v712-and-v740) to have control over hash joins for tables. It is enabled by default (`ON`). If you are sure that you do not need to select hash joins between tables in your execution plan, you can modify the variable to `OFF` to reduce the possibility of execution plan rollbacks and improve system stability.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_hash_join-new-in-v656-v712-and-v740).

* Memory control for the statistics cache is generally available (GA) [#45367](https://github.com/pingcap/tidb/issues/45367) @[hawkingrei](https://github.com/hawkingrei)

    TiDB instances can cache table statistics to accelerate execution plan generation and improve SQL performance. Starting from v6.1.0, TiDB introduces the system variable [`tidb_stats_cache_mem_quota`](https://github.com/system-variables.md#tidb_stats_cache_mem_quota-new-in-v610). By configuring this system variable, you can set a memory usage limit for the statistics cache. When the cache reaches its limit, TiDB automatically evicts inactive cache entries, helping control instance memory usage and improve stability.

    Starting from v7.4.0, this feature becomes generally available (GA).
    
    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stats_cache_mem_quota-new-in-v610).
