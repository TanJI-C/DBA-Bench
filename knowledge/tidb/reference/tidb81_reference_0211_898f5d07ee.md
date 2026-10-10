# Binlog event filter overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-binlog-event-filter.md`
- Source Title: `TiDB Data Migration Binlog Event Filter`
- Source Heading Path: `TiDB Data Migration Binlog Event Filter`
- Source Line Ranges: `5-9`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `binlog`, `event filter`, `schema pattern`, `table pattern`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0211_898f5d07ee`
- Source ID: `tidb-docs-8.1:dm/dm-binlog-event-filter.md#tidb-data-migration-binlog-event-filter`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `59bfe2782472c9a0dfdd9845b2d292512ecd5a916a198401d08f0cbc7c2671a6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter#tidb-data-migration-binlog-event-filter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-binlog-event-filter.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs an overview of DM binlog event filtering and what kinds of binlog events it can filter for specific schemas or tables.
- Retrieval Keywords: TiDB Data Migration binlog event filter, DM binlog event filter overview, filter out TRUNCATE TABLE, filter out INSERT events, block and report errors, only receive specified types of binlog events, schema pattern, table pattern, block and allow lists
- Follow-up Guidance: The source also points to configuration details and explains that binlog event filtering is more fine-grained than block and allow lists.
- Classification Note: This is reference content because it defines the binlog event filter feature, its purpose, and example event types without giving procedural steps.

## Official Source Content

# TiDB Data Migration Binlog Event Filter

TiDB Data Migration (DM) provides the binlog event filter feature to filter out, block and report errors, or only receive specified types of binlog events for some schemas or tables. For example, you can filter out all `TRUNCATE TABLE` or `INSERT` events. The binlog event filter feature is more fine-grained than the [block and allow lists](https://docs.pingcap.com/tidb/stable/dm/dm-block-allow-table-lists) feature.
