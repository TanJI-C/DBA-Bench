# DM binlog event filter configuration and rule behavior

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/filter-binlog-event.md`
- Source Title: `Filter Binlog Events`
- Source Heading Path: `Filter Binlog Events | Filter Binlog Events > Configuration`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `binlog`, `event-filter`, `task-configuration`, `schema-pattern`, `table-pattern`, `events`, `sql-pattern`, `allowlist`, `blocklist`, `ddl`, `dml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0111_d4d4a01d89`
- Source ID: `tidb-docs-8.1:filter-binlog-event.md#filter-binlog-events`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9cba24e637dc34970d1545f993e250035c24503d554a458ed4bb03597e79a77`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/filter-binlog-event#filter-binlog-events
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/filter-binlog-event.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM task configuration format for binlog event filtering and the rule behavior of `schema-pattern`, `table-pattern`, `events`, `sql-pattern`, and `action`.
- Retrieval Keywords: DM binlog event filter configuration, filters, schema-pattern, table-pattern, events, sql-pattern, action, Do, Ignore, Ignore has higher priority over Do, all dml, all ddl, none ddl, none dml, truncate table, drop table, create database, drop database, create table, create index, rename table, alter table
- Follow-up Guidance: The source also points to migration scenario documents for detailed replication instructions.
- Classification Note: This is classified as configuration because the official content defines the `filter` structure in a DM task configuration file and explains supported event names and rule precedence.

## Official Source Content

# Filter Binlog Events

This document describes how to filter binlog events when you use DM to perform continuous incremental data replication. For the detailed replication instructions, refer to the following documents by scenarios:

- [Migrate Small Datasets from MySQL to TiDB](https://docs.pingcap.com/tidb/stable/migrate-small-mysql-to-tidb)
- [Migrate Large Datasets from MySQL to TiDB](https://docs.pingcap.com/tidb/stable/migrate-large-mysql-to-tidb)
- [Migrate and Merge MySQL Shards of Small Datasets to TiDB](https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb)
- [Migrate and Merge MySQL Shards of Large Datasets to TiDB](https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb)
## Configuration

To use binlog event filter, add a `filter` to the task configuration file of DM, as shown below:

```yaml
filters:
  rule-1:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    events: ["truncate table", "drop table"]
    sql-pattern: ["^DROP\\s+PROCEDURE", "^CREATE\\s+PROCEDURE"]
    action: Ignore
```

- `schema-pattern`/`table-pattern`: Filters matching schemas or tables
- `events`: Filters binlog events. Supported events are listed in the table below:

  | Event           | Category | Description                       |
  | --------------- | ---- | --------------------------|
  | all             |      | Includes all events            |
  | all dml         |      | Includes all DML events        |
  | all ddl         |      | Includes all DDL events        |
  | none            |      | Includes no event          |
  | none ddl        |      | Excludes all DDL events      |
  | none dml        |      | Excludes all DML events      |
  | insert          | DML  | Insert DML event      |
  | update          | DML  | Update DML event      |
  | delete          | DML  | Delete DML event      |
  | create database | DDL  | Create database event |
  | drop database   | DDL  | Drop database event   |
  | create table    | DDL  | Create table event    |
  | create index    | DDL  | Create index event    |
  | drop table      | DDL  | Drop table event      |
  | truncate table  | DDL  | Truncate table event  |
  | rename table    | DDL  | Rename table event    |
  | drop index      | DDL  | Drop index event      |
  | alter table     | DDL  | Alter table event     |

- `sql-pattern`: Filters specified DDL SQL statements. The matching rule supports using a regular expression.
- `action`: `Do` or `Ignore`

    - `Do`: the allow list. A binlog event is replicated if meeting either of the following two conditions:

        - The event matches the rule setting.
        - sql-pattern has been specified and the SQL statement of the event matches any of the sql-pattern options.

    - `Ignore`: the block list. A binlog event is filtered out if meeting either of the following two conditions:

        - The event matches the rule setting.
        - sql-pattern has been specified and the SQL statement of the event matches any of the sql-pattern options.

    If both `Do` and `Ignore` are configured, `Ignore` has higher priority over `Do`. That is, an event satisfying both `Ignore` and `Do` conditions will be filtered out.
