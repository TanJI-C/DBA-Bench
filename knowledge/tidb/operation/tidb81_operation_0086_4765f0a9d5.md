# DM binlog filter usage examples

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-binlog-event-filter.md`
- Source Title: `TiDB Data Migration Binlog Event Filter`
- Source Heading Path: `TiDB Data Migration Binlog Event Filter > Usage examples | TiDB Data Migration Binlog Event Filter > Usage examples > Filter all sharding deletion operations | TiDB Data Migration Binlog Event Filter > Usage examples > Only migrate sharding DML statements | TiDB Data Migration Binlog Event Filter > Usage examples > Filter out the SQL statements that TiDB does not support | TiDB Data Migration Binlog Event Filter > Usage examples > Filter out the SQL statements that the TiDB parser does not support`
- Source Line Ranges: `98-178`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `sharding`, `dml`, `ddl`, `ignore`, `global filtering`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0086_4765f0a9d5`
- Source ID: `tidb-docs-8.1:dm/dm-binlog-event-filter.md#usage-examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `77b5c1850ee4e4707e55e9f45edd7c3e6316e157111b9fa293abfc1b321504ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter#usage-examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-binlog-event-filter.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for concrete DM binlog filter examples such as filtering sharding deletion operations, migrating only sharding DML, or ignoring unsupported `PROCEDURE` or `PARTITION` SQL statements.
- Retrieval Keywords: Filter all sharding deletion operations, Only migrate sharding DML statements, filter-table-rule, filter-schema-rule, do-table-rule, do-schema-rule, filter-procedure-rule, filter-partition-rule, events: ["truncate table", "drop table", "delete"], events: ["create table", "all dml"], events: ["create database"], sql-pattern: ["^DROP\\s+PROCEDURE", "^CREATE\\s+PROCEDURE"], schema-pattern: "*", ALTER\s+TABLE[\s\S]*ADD\s+PARTITION, ALTER\s+TABLE[\s\S]*DROP\s+PARTITION, global filtering rule
- Follow-up Guidance: The source notes that `CREATE DATABASE/TABLE` is migrated so DML statements can be migrated after the schema and table are created, and unsupported parser cases require the global filtering rule `schema-pattern: "*"`.
- Classification Note: This is operation content because it demonstrates practical filter rule examples for sharding and unsupported SQL handling using specific YAML configurations.

## Official Source Content

## Usage examples

This section shows the usage examples in the scenario of sharding (sharded schemas and tables).
### Filter all sharding deletion operations

To filter out all deletion operations, configure the following two filtering rules:

- `filter-table-rule` filters out the `TRUNCATE TABLE`, `DROP TABLE` and `DELETE STATEMENT` operations of all tables that match the `test_*`.`t_*` pattern.
- `filter-schema-rule` filters out the `DROP DATABASE` operation of all schemas that match the `test_*` pattern.

```yaml
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
### Only migrate sharding DML statements

To only migrate sharding DML statements, configure the following two filtering rules:

- `do-table-rule` only migrates the `CREATE TABLE`, `INSERT`, `UPDATE` and `DELETE` statements of all tables that match the `test_*`.`t_*` pattern.
- `do-schema-rule` only migrates the `CREATE DATABASE` statement of all schemas that match the `test_*` pattern.

> **Note:**
>
> The reason why the `CREATE DATABASE/TABLE` statement is migrated is that you can migrate DML statements only after the schema and table are created.

```yaml
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
### Filter out the SQL statements that TiDB does not support

To filter out the `PROCEDURE` statements that TiDB does not support, configure the following `filter-procedure-rule`:

```yaml
filters:
  filter-procedure-rule:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    sql-pattern: ["^DROP\\s+PROCEDURE", "^CREATE\\s+PROCEDURE"]
    action: Ignore
```

`filter-procedure-rule` filters out the `^CREATE\\s+PROCEDURE` and `^DROP\\s+PROCEDURE` statements of all tables that match the `test_*`.`t_*` pattern.
### Filter out the SQL statements that the TiDB parser does not support

For the SQL statements that the TiDB parser does not support, DM cannot parse them and get the `schema`/`table` information. So you must use the global filtering rule: `schema-pattern: "*"`.

> **Note:**
>
> To avoid filtering out data that need to be migrated, you must configure the global filtering rule as strictly as possible.

To filter out the `PARTITION` statements that the TiDB parser (of some version) does not support, configure the following filtering rule:

```yaml
filters:
  filter-partition-rule:
    schema-pattern: "*"
    sql-pattern: ["ALTER\\s+TABLE[\\s\\S]*ADD\\s+PARTITION", "ALTER\\s+TABLE[\\s\\S]*DROP\\s+PARTITION"]
    action: Ignore
```
