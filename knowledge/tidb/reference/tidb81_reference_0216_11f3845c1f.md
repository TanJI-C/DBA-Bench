# DM special DDL handling for shard merge and online DDL

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-ddl-compatible.md`
- Source Title: `Special Handling of DM DDLs`
- Source Heading Path: `Special Handling of DM DDLs > Shard merge migration tasks | Special Handling of DM DDLs > Online DDL`
- Source Line Ranges: `137-143`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `ddl`, `shard-merge`, `pessimistic-mode`, `optimistic-mode`, `online-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0216_11f3845c1f`
- Source ID: `tidb-docs-8.1:dm/dm-ddl-compatible.md#shard-merge-migration-tasks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c610f1eb82461afb2e2e64d232a2d09c7d010f84c9668a48b123cfe7780d429`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-ddl-compatible#shard-merge-migration-tasks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-ddl-compatible.md

## Retrieval Guidance

- Use When: Use this chunk when looking for where the documentation states that DM handles DDL replication differently for shard merge migration tasks and Online DDL scenarios.
- Retrieval Keywords: Shard merge migration tasks, pessimistic mode, optimistic mode, DDL replication is different, Pessimistic Mode, Optimistic Mode, Online DDL, DDL events in a special way, Migrate from Databases that Use GH-ost/PT-osc
- Follow-up Guidance: The source points to the Pessimistic Mode, Optimistic Mode, and Migrate from Databases that Use GH-ost/PT-osc pages for details.
- Classification Note: This is reference content because it identifies special DDL handling contexts in DM and directs readers to the corresponding detailed feature documentation.

## Official Source Content

## Shard merge migration tasks

When DM merges and migrates tables in pessimistic or optimistic mode, the behavior of DDL replication is different from that in other scenarios. For details, refer to [Pessimistic Mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic) and [Optimistic Mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic).
## Online DDL

The Online DDL feature also handles DDL events in a special way. For details, refer to [Migrate from Databases that Use GH-ost/PT-osc](https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl).
