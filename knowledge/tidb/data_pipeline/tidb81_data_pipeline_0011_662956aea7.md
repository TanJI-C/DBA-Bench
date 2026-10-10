# DM shard merge overview, restrictions, configuration, and manual DDL lock handling

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-shard-merge.md`
- Source Title: `TiDB Data Migration Shard Merge`
- Source Heading Path: `TiDB Data Migration Shard Merge | TiDB Data Migration Shard Merge > Restrictions | TiDB Data Migration Shard Merge > Configure parameters | TiDB Data Migration Shard Merge > Handle sharding DDL locks manually`
- Source Line Ranges: `5-30`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `shard-merge`, `sharded-tables`, `dml`, `ddl`, `task-configuration`, `pessimistic-mode`, `optimistic-mode`, `ddl-locks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0011_662956aea7`
- Source ID: `tidb-docs-8.1:dm/dm-shard-merge.md#tidb-data-migration-shard-merge`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `74b4945adeb2190f9fd4588e584ea1651a1022ab8a51e46a282a19724aa0340f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-shard-merge#tidb-data-migration-shard-merge
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-shard-merge.md

## Retrieval Guidance

- Use When: Use this chunk when looking for DM shard merge basics, its limited support restrictions, the `shard-mode` task configuration, or mention of manually handling sharding DDL locks.
- Retrieval Keywords: TiDB Data Migration Shard Merge, DM shard merge, merge the DML and DDL data, upstream MySQL/MariaDB sharded tables, downstream TiDB tables, Restrictions, Sharding DDL usage Restrictions in the pessimistic mode, Sharding DDL usage Restrictions in the optimistic mode, Configure parameters, task configuration file, shard-mode, pessimistic, optimistic, Handle sharding DDL locks manually, manually handling sharding DDL locks
- Follow-up Guidance: The source points to detailed restriction pages for pessimistic and optimistic modes and to the page for manually handling sharding DDL locks.
- Classification Note: This is classified under the DM data pipeline component because the content describes sharded table DML and DDL merge behavior, task configuration, and DDL lock handling for TiDB Data Migration.

## Official Source Content

# TiDB Data Migration Shard Merge

TiDB Data Migration (DM) supports merging the DML and DDL data in the upstream MySQL/MariaDB sharded tables and migrating the merged data to the downstream TiDB tables.

If you need to migrate and merge MySQL shards of small datasets to TiDB, refer to [this tutorial](https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb).
## Restrictions

Currently, the shard merge feature is supported only in limited scenarios. For details, refer to [Sharding DDL usage Restrictions in the pessimistic mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#restrictions) and [Sharding DDL usage Restrictions in the optimistic mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic#restrictions).
## Configure parameters

In the task configuration file, set `shard-mode` to `pessimistic`:

```yaml
shard-mode: "pessimistic"
# The shard merge mode. Optional modes are ""/"pessimistic"/"optimistic". The "" mode is used by default
# which means sharding DDL merge is disabled. If the task is a shard merge task, set it to the "pessimistic"
# mode. After getting a deep understanding of the principles and restrictions of the "optimistic" mode, you
# can set it to the "optimistic" mode.
```
## Handle sharding DDL locks manually

In some abnormal scenarios, you need to [handle sharding DDL Locks manually](https://docs.pingcap.com/tidb/stable/dm/manually-handling-sharding-ddl-locks).
