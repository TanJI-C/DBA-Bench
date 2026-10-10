# DM shard migration planning, archiving, and shard DDL modes

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-best-practices.md`
- Source Title: `TiDB Data Migration (DM) Best Practices`
- Source Heading Path: `TiDB Data Migration (DM) Best Practices > Before data migration > Key points for MySQL shards | TiDB Data Migration (DM) Best Practices > Before data migration > Key points for MySQL shards > Splitting and merging | TiDB Data Migration (DM) Best Practices > Before data migration > Key points for MySQL shards > The pessimistic mode and the optimistic mode | TiDB Data Migration (DM) Best Practices > Before data migration > Other restrictions and impact`
- Source Line Ranges: `80-106`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `mysql-shards`, `merge-migration`, `data-archiving`, `partitioning`, `placement-rules`, `pessimistic-mode`, `optimistic-mode`, `relay-log`, `schema-changes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0008_ec98c1e670`
- Source ID: `tidb-docs-8.1:dm/dm-best-practices.md#key-points-for-mysql-shards`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3e1bee570474a2eaa61eb96dec5b79933330f6bcaa49ec5f6d6ded11115cae70`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-best-practices#key-points-for-mysql-shards
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when planning DM migration and merge of MySQL shards, considering data archiving with partitioning and placement rules, or comparing pessimistic mode and optimistic mode for shard DDL handling.
- Retrieval Keywords: Key points for MySQL shards, migrate and merge MySQL shards of small datasets to TiDB, Splitting and merging, data archiving, placement rules, partition, TiDB does not support Table Rebuild operations yet, pessimistic mode, optimistic mode, upstream shard schemas, block DML writing to downstream databases, upstream Binlog to be cleaned up, enable the relay log, Use the relay log, incompatible formats, incremental column has a default value
- Follow-up Guidance: The source explains that pessimistic mode is the default, relay log can help when long schema changes risk upstream binlog cleanup, and optimistic mode avoids blocking but can stop on incompatible formats that require manual resolution.
- Classification Note: This is classified as data_pipeline because the content focuses on shard merge migration behavior, schema change handling modes, relay log use, and data archiving considerations during migration.

## Official Source Content

### Key points for MySQL shards
#### Splitting and merging

It is recommended that you use DM to [migrate and merge MySQL shards of small datasets to TiDB](https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb).

Besides data merging, another typical scenario is data archiving. Data is constantly being written. As time goes by, large amounts of data gradually change from hot data to warm or even cold data. Fortunately, in TiDB, you can set different [placement rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) for data. The minimum granularity of the rules is [a partition](https://docs.pingcap.com/tidb/stable/partitioned-table).

Therefore, it is recommended that for write-intensive scenarios, you need to evaluate from the beginning whether you need to archive data and store hot and cold data on different media separately. If you need to archive data, you can set the partitioning rules before migration (TiDB does not support Table Rebuild operations yet). It saves you from the need to recreate tables and import data in future.
#### The pessimistic mode and the optimistic mode

DM uses the pessimistic mode by default. In scenarios of migrating and merging MySQL shards, changes in upstream shard schemas can block DML writing to downstream databases. You need to wait until all the schemas are changed and have the same structure, and then continue the migration from the breakpoint.

- If the upstream schema changes take a long time, it might cause the upstream Binlog to be cleaned up. You can enable the relay log to avoid this problem. For more information, see [Use the relay log](#use-the-relay-log).

- If you do not want to block data write due to upstream schema changes, consider using the optimistic mode. In this case, DM will not block the data migration even when it spots changes in the upstream shard schemas, but will continue to migrate the data. However, if DM spots incompatible formats in upstream and downstream, the migration task will stop. You need to resolve this issue manually.

The following table summarizes the pros and cons of optimistic mode and pessimistic modes.

| Scenario | Pros | Cons |
| :--- | :--- | :--- |
| Pessimistic mode (Default) | It can ensure that the data migrated to the downstream will not go wrong.  | If there are a large number of shards, the migration task will be blocked for a long time, or even stop if the upstream binlogs have been cleaned up. You can enable the relay log to avoid this problem. For more information, see [Use the relay log](#use-the-relay-log). |
| Optimistic mode| Upstream schema changes will not cause data migration latency.  | In this mode, ensure that schema changes are compatible (check whether the incremental column has a default value). It is possible that the inconsistent data can be overlooked. For more information, see [Merge and Migrate Data from Sharded Tables in Optimistic Mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic#restrictions).|
### Other restrictions and impact
