# Performance Schema tables and extensions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-schema/performance-schema.md`
- Source Title: `Performance Schema`
- Source Heading Path: `Performance Schema | Performance Schema > Tables for MySQL compatibility | Performance Schema > Tables that are TiDB extensions`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`
- Topic Tags: `performance_schema`, `mysql_compatibility`, `system_metadata`, `table_reference`, `profiling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0477_e60a58bf4b`
- Source ID: `tidb-docs-8.1:performance-schema/performance-schema.md#performance-schema`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2d785d717b24ca2a93ecae98036e470a07a4c966c0c120249596eea1f596bc3d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-schema/performance-schema#performance-schema
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-schema/performance-schema.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which Performance Schema tables TiDB provides for MySQL compatibility and which tables are TiDB-specific extensions, including profiling-related table names.
- Retrieval Keywords: Performance Schema, performance schema tables, Tables for MySQL compatibility, Tables that are TiDB extensions, events_stages_current, events_stages_history, events_stages_history_long, events_statements_current, events_statements_history, events_statements_history_long, events_statements_summary_by_digest, events_transactions_current, events_transactions_history, events_transactions_history_long, global_status, prepared_statements_instances, session_connect_attrs, session_status, session_variables, setup_actors, setup_consumers, setup_instruments, setup_objects, pd_profile_allocs, pd_profile_block, pd_profile_cpu, pd_profile_goroutines, pd_profile_memory, pd_profile_mutex, tidb_profile_allocs, tidb_profile_block, tidb_profile_cpu, tidb_profile_goroutines, tidb_profile_memory, tidb_profile_mutex, tikv_profile_cpu
- Follow-up Guidance: The source notes that `session_connect_attrs` provides connection attributes for sessions.
- Classification Note: This chunk is reference material because it enumerates Performance Schema table names and distinguishes MySQL-compatible tables from TiDB extension tables.

## Official Source Content

# Performance Schema

TiDB implements performance schema tables for MySQL compatibility.
## Tables for MySQL compatibility

| Table name                                                                                       | Description                                               |
|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| `events_stages_current`                                                                          |                                                           |
| `events_stages_history`                                                                          |                                                           |
| `events_stages_history_long`                                                                     |                                                           |
| `events_statements_current`                                                                      |                                                           |
| `events_statements_history`                                                                      |                                                           |
| `events_statements_history_long`                                                                 |                                                           |
| `events_statements_summary_by_digest`                                                            |                                                           |
| `events_transactions_current`                                                                    |                                                           |
| `events_transactions_history`                                                                    |                                                           |
| `events_transactions_history_long`                                                               |                                                           |
| `global_status`                                                                                  |                                                           |
| `prepared_statements_instances`                                                                  |                                                           |
| [`session_connect_attrs`](https://docs.pingcap.com/tidb/stable/performance-schema/performance-schema-session-connect-attrs)       | Provides connection attributes for sessions.              |
| `session_status`                                                                                 |                                                           |
| `session_variables`                                                                              |                                                           |
| `setup_actors`                                                                                   |                                                           |
| `setup_consumers`                                                                                |                                                           |
| `setup_instruments`                                                                              |                                                           |
| `setup_objects`                                                                                  |                                                           |
## Tables that are TiDB extensions

| Table name                                                                                       | Description                                               |
|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| `pd_profile_allocs`                                                                              |                                                           |
| `pd_profile_block`                                                                               |                                                           |
| `pd_profile_cpu`                                                                                 |                                                           |
| `pd_profile_goroutines`                                                                          |                                                           |
| `pd_profile_memory`                                                                              |                                                           |
| `pd_profile_mutex`                                                                               |                                                           |
| `tidb_profile_allocs`                                                                            |                                                           |
| `tidb_profile_block`                                                                             |                                                           |
| `tidb_profile_cpu`                                                                               |                                                           |
| `tidb_profile_goroutines`                                                                        |                                                           |
| `tidb_profile_memory`                                                                            |                                                           |
| `tidb_profile_mutex`                                                                             |                                                           |
| `tikv_profile_cpu`                                                                               |                                                           |
