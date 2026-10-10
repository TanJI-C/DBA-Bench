# DM safe mode limitations and risks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-safe-mode.md`
- Source Title: `DM Safe Mode`
- Source Heading Path: `DM Safe Mode > Notes for safe mode`
- Source Line Ranges: `94-102`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `safe-mode`, `performance-overhead`, `data-loss`, `primary-key`, `unique-index`, `shard-merge`, `data-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0104_df4314a030`
- Source ID: `tidb-docs-8.1:dm/dm-safe-mode.md#notes-for-safe-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `10529a54bf783bc276213dfef12cfb5cde1e289f61f20d9c82df34dafa05f4ea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-safe-mode#notes-for-safe-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-safe-mode.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the limitations, overhead, and data consistency risks of running DM safe mode during the entire replication process.
- Retrieval Keywords: Notes for safe mode, performance overhead, DELETE + REPLACE, data loss, downstream, primary key, unique index, merge and migrate shards, primary key conflict, unique key conflicts, data inconsistency, duplicate records
- Follow-up Guidance: The source summarizes that safe mode can be enabled to ignore data duplication when the upstream has duplicate primary keys and the application tolerates loss of duplicate records and performance overhead.
- Classification Note: This is classified as operation because the content gives operational cautions and risk notes for using safe mode in ongoing replication.

## Official Source Content

## Notes for safe mode

If you want to enable safe mode during the entire replication process for safety reasons, be aware of the following:

- **Incremental replication in safe mode consumes extra overhead.** Frequent `DELETE` + `REPLACE` operations result in frequent changes to primary keys or unique indexes, which creates a greater performance overhead than executing `UPDATE` statements only.
- **Safe mode forces the replacement of records with the same primary key, which might result in data loss in the downstream.** When you merge and migrate shards from the upstream to the downstream, incorrect configuration might lead to a large number of primary key or unique key conflicts. If safe mode is enabled in this situation, the downstream might lose lots of data without showing any exception, resulting in severe data inconsistency.
- **Safe mode relies on the primary key or unique index to detect conflicts.** If the downstream table has no primary key or unique index, DM cannot use `REPLACE` to replace and insert records. In this case, even if safe mode is enabled and DM rewrites `INSERT` to `REPLACE` statements, duplicate records are still inserted into the downstream.

In summary, if the upstream database has data with duplicate primary keys, and your application tolerates loss of duplicate records and performance overhead, you can enable safe mode to ignore data duplication.
