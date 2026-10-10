# TTL compatibility with tools and flashback SQL

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/time-to-live.md`
- Source Title: `Periodically Delete Data Using TTL (Time to Live)`
- Source Heading Path: `Periodically Delete Expired Data Using TTL (Time to Live) > Compatibility with TiDB tools | Periodically Delete Expired Data Using TTL (Time to Live) > Compatibility with SQL`
- Source Line Ranges: `235-252`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `lightning`, `ticdc`, `sql`
- Topic Tags: `ttl`, `compatibility`, `backup-restore`, `import`, `replication`, `flashback`, `ttl-enable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0957_61863a8e1d`
- Source ID: `tidb-docs-8.1:time-to-live.md#compatibility-with-tidb-tools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `335c3aff3fd03f3f33373e661118a1331b6173443a746ad92789787815dc9b78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/time-to-live#compatibility-with-tidb-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/time-to-live.md

## Retrieval Guidance

- Use When: Use this chunk when you need compatibility behavior for TTL with BR, TiDB Lightning, TiCDC, or FLASHBACK SQL statements, especially how `TTL_ENABLE` or `TIDB_TTL_JOB_ENABLE` changes after those operations.
- Retrieval Keywords: Compatibility with TiDB tools, Backup & Restore (BR), TiDB Lightning, TiCDC, FLASHBACK TABLE, FLASHBACK DATABASE, FLASHBACK CLUSTER, TTL_ENABLE, TIDB_TTL_JOB_ENABLE, downstream TTL_ENABLE OFF, minimum supported version
- Follow-up Guidance: It lists minimum supported versions for BR v6.6.0, TiDB Lightning v6.6.0, and TiCDC v7.0.0, and states when `TTL_ENABLE` is set to `OFF` or when `TIDB_TTL_JOB_ENABLE` is set to `OFF`.
- Classification Note: This is classified as reference because the content is a compatibility matrix and behavior summary for TTL interactions with tools and SQL features.

## Official Source Content

## Compatibility with TiDB tools

TTL can be used with other TiDB migration, backup, and recovery tools.

| Tool name | Minimum supported version | Description |
| --- | --- | --- |
| Backup & Restore (BR) | v6.6.0 | After you restore data using BR, the `TTL_ENABLE` attribute of the tables will be set to `OFF`. This prevents TiDB from immediately deleting expired data after backup and restore. You need to manually turn on the `TTL_ENABLE` attribute to re-enable TTL for each table. |
| TiDB Lightning | v6.6.0 | After you import data using TiDB Lighting, the `TTL_ENABLE` attribute of the imported table will be set to `OFF`.  This prevents TiDB from immediately deleting expired data after importing. You need to manually turn on the `TTL_ENABLE` attribute to re-enable TTL for each table. |
| TiCDC | v7.0.0 | The `TTL_ENABLE` attribute in the downstream will be automatically set to `OFF`. The upstream TTL deletions will be synchronized to the downstream. Therefore, to prevent duplicate deletions, the `TTL_ENABLE` attribute of the downstream tables will be forcibly set to `OFF`. |
## Compatibility with SQL

| Feature name | Description |
| :-- | :---- |
| [`FLASHBACK TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-table) |  `FLASHBACK TABLE` will set the `TTL_ENABLE` attribute of the tables to `OFF`. This prevents TiDB from immediately deleting expired data after the flashback. You need to manually turn on the `TTL_ENABLE` attribute to re-enable TTL for each table. |
| [`FLASHBACK DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-database) | `FLASHBACK DATABASE` will set the `TTL_ENABLE` attribute of the tables to `OFF`, and the `TTL_ENABLE` attribute will not be modified. This prevents TiDB from immediately deleting expired data after the flashback. You need to manually turn on the `TTL_ENABLE` attribute to re-enable TTL for each table. |
| [`FLASHBACK CLUSTER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) | `FLASHBACK CLUSTER` will set the system variable [`TIDB_TTL_JOB_ENABLE`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ttl_job_enable-new-in-v650) to `OFF` and do not change the value of the `TTL_ENABLE` attribute. |
