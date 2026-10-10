# DM binlog event filter application scenarios

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/filter-binlog-event.md`
- Source Title: `Filter Binlog Events`
- Source Heading Path: `Filter Binlog Events > Application scenarios | Filter Binlog Events > Application scenarios > Filter out all sharding deletion operations | Filter Binlog Events > Application scenarios > Migrate only DML operations of sharded schemas and tables | Filter Binlog Events > Application scenarios > Filter out SQL statements not supported by TiDB | Filter Binlog Events > See also`
- Source Line Ranges: `68-124`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `binlog`, `event-filter`, `sharding`, `delete-filtering`, `dml-only`, `sql-pattern`, `unsupported-sql`, `procedures`, `partitions`, `migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0024_fc8dea1ed4`
- Source ID: `tidb-docs-8.1:filter-binlog-event.md#application-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `83da39c46ca66026888fd23d7697956d1c9ff234ce953383d777306cce0033cd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/filter-binlog-event#application-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/filter-binlog-event.md

## Retrieval Guidance

- Use When: Use this chunk when you need example DM binlog event filter rules for sharding deletion operations, DML-only migration, or filtering SQL statements not supported by TiDB.
- Retrieval Keywords: Filter out all sharding deletion operations, filter-table-rule, filter-schema-rule, drop database, truncate table, drop table, delete, Migrate only DML operations of sharded schemas and tables, do-table-rule, do-schema-rule, create table, all dml, create database, Filter out SQL statements not supported by TiDB, filter-procedure-rule, DROP PROCEDURE, CREATE PROCEDURE, ADD PARTITION, DROP PARTITION, global filtering rule as strictly as possible, Filter Binlog Events Using SQL Expressions
- Follow-up Guidance: The source includes a warning to configure the global filtering rule as strictly as possible to avoid filtering out data that needs to be migrated and links to Filter Binlog Events Using SQL Expressions.
- Classification Note: This is classified as data_pipeline because the official content presents migration and replication filtering scenarios for DM, including sharded schemas and unsupported SQL handling.

## Official Source Content

## Application scenarios

This section describes the application scenarios of binlog event filter.
### Filter out all sharding deletion operations

To filter out all deletion operations, configure a `filter-table-rule` and a `filter-schema-rule`, as shown below:

```
filters:
  filter-table-rule:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    events: ["truncate table", "drop table", "delete"]
    action: Ignore
  filter-schema-rule:
    schema-pattern: "test_*"
    events: ["drop database"]
    action: Ignore
```
### Migrate only DML operations of sharded schemas and tables

To replicate only DML statements, configure two `Binlog event filter rule`, as shown below:

```
filters:
  do-table-rule:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    events: ["create table", "all dml"]
    action: Do
  do-schema-rule:
    schema-pattern: "test_*"
    events: ["create database"]
    action: Do
```
### Filter out SQL statements not supported by TiDB

To filter out SQL statements not supported by TiDB, configure a `filter-procedure-rule`, as shown below:

```
filters:
  filter-procedure-rule:
    schema-pattern: "*"
    sql-pattern: [".*\\s+DROP\\s+PROCEDURE", ".*\\s+CREATE\\s+PROCEDURE", "ALTER\\s+TABLE[\\s\\S]*ADD\\s+PARTITION", "ALTER\\s+TABLE[\\s\\S]*DROP\\s+PARTITION"]
    action: Ignore
```

> **Warning:**
>
> To avoid filtering out data that needs to be migrated, configure the global filtering rule as strictly as possible.
## See also

[Filter Binlog Events Using SQL Expressions](https://docs.pingcap.com/tidb/stable/filter-dml-event)
