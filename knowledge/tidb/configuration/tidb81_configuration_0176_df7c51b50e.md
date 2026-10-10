# TiCDC event filter rules for DDL events

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-ddl.md`
- Source Title: `Changefeed DDL Replication`
- Source Heading Path: `Changefeed DDL Replication > DDL replication considerations > Notes on using event filter rules to filter DDL events`
- Source Line Ranges: `111-139`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `sql`
- Topic Tags: `event filters`, `ddl filtering`, `dml replication`, `schema consistency`, `version-specific behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0176_df7c51b50e`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-ddl.md#notes-on-using-event-filter-rules-to-filter-ddl-events`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `41cfcdd947e2e7c154a7b023640ef4f40662d8968210001c00fe2f730d5b2989`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-ddl#notes-on-using-event-filter-rules-to-filter-ddl-events
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when understanding how TiCDC event filter rules affect DDL events such as `CREATE TABLE`, `DROP TABLE`, `TRUNCATE TABLE`, and `RENAME TABLE`, and how that interacts with DML replication.
- Retrieval Keywords: Notes on using event filter rules to filter DDL events, filter.event-filters, ignore-event, create table, drop table, truncate table, rename table, DDL behavior, DML behavior, schema consistency, upstream and downstream database schemas remain consistent, versions earlier than v6.5.8, v7.1.4, and v7.5.1
- Follow-up Guidance: The note says to use the event filter to filter DDL events with caution and ensure schema consistency, and it states that for versions earlier than v6.5.8, v7.1.4, and v7.5.1, filtering DDL events involving table creation or deletion affects DML replication.
- Classification Note: This is classified under configuration because the content explains changefeed `filter` and `filter.event-filters` behavior for DDL event filtering and its replication effects.

## Official Source Content

### Notes on using event filter rules to filter DDL events

If a filtered DDL statement involves table creation or deletion, TiCDC only filters out the DDL statement without affecting the replication behavior of DML statements. The following is an example.

Assume that the configuration file of your changefeed is as follows:

```toml
[filter]
rules = ['test.t*']

[[filter.event-filters]]
matcher = ["test.t1"] # This filter rule applies only to the t1 table in the test database.
ignore-event = ["create table", "drop table", "truncate table", "rename table"]
```

| DDL | DDL behavior | DML behavior | Explanation |
| --- | --- | --- | --- |
| `CREATE TABLE test.t1 (id INT, name VARCHAR(50));` | Ignore | Replicate | `test.t1` matches the event filter rule, so the `CREATE TABLE` event is ignored. The replication of DML events remains unaffected. |
| `CREATE TABLE test.t2 (id INT, name VARCHAR(50));` | Replicate | Replicate | `test.t2` does not match the event filter rule. |
| `CREATE TABLE test.ignore (id INT, name VARCHAR(50));` | Ignore | Ignore | `test.ignore` matches the event filter rule, so both DDL and DML events are ignored. |
| `DROP TABLE test.t1;` | Ignore | - | `test.t1` matches the event filter rule, so the `DROP TABLE` event is ignored. Because the table is deleted, TiCDC no longer replicates DML events for `t1`. |
| `TRUNCATE TABLE test.t1;` | Ignore | Replicate | `test.t1` matches the event filter rule, so the `TRUNCATE TABLE` event is ignored. The replication of DML events remains unaffected. |
| `RENAME TABLE test.t1 TO test.t2;` | Ignore | Replicate | `test.t1` matches the event filter rule, so the `RENAME TABLE` event is ignored. The replication of DML events remains unaffected. |
| `RENAME TABLE test.t1 TO test.ignore;` | Ignore | Ignore | `test.t1` matches the event filter rule, so the `RENAME TABLE` event is ignored. `test.ignore` matches the event filter rule, so both DDL and DML events are ignored. |

> **Note:**
>
> - When replicating data to a database, use the event filter to filter DDL events with caution. Ensure that the upstream and downstream database schemas remain consistent during replication. Otherwise, TiCDC might report errors or cause undefined replication behavior.
> - For versions earlier than v6.5.8, v7.1.4, and v7.5.1, using the event filter to filter DDL events involving table creation or deletion affects DML replication. It is not recommended to use this feature in these versions.
