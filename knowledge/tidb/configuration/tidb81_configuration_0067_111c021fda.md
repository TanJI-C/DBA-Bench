# Configure DM binlog event filters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-binlog-event-filter.md`
- Source Title: `TiDB Data Migration Binlog Event Filter`
- Source Heading Path: `TiDB Data Migration Binlog Event Filter > Configure the binlog event filter | TiDB Data Migration Binlog Event Filter > Parameter descriptions`
- Source Line Ranges: `10-97`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `yaml`, `filter rules`, `events`, `sql pattern`, `action`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0067_111c021fda`
- Source ID: `tidb-docs-8.1:dm/dm-binlog-event-filter.md#configure-the-binlog-event-filter`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6df6e5cacd2d9c57c8314fc4e3c1eb472e2e5063bd8d129042336aff9989d679`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter#configure-the-binlog-event-filter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-binlog-event-filter.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the DM task or source configuration syntax, supported filter parameters, event names, wildcard and regular expression matching rules, or `Do`/`Ignore`/`Error` behavior.
- Retrieval Keywords: filters:, schema-pattern, table-pattern, events, sql-pattern, action, Do, Ignore, Error, all dml, all ddl, incompatible ddl changes, truncate table, drop table, ^DROP\s+PROCEDURE, ^CREATE\s+PROCEDURE, wildcard matching, regular expressions, When multiple rules match the same table
- Follow-up Guidance: The source provides a YAML example, lists supported `events`, and states that matching rules are applied sequentially with `Ignore` higher priority than `Error`, and `Error` higher priority than `Do`.
- Classification Note: This is configuration content because it specifies the YAML fields, allowed values, matching syntax, and rule precedence for configuring DM binlog event filters.

## Official Source Content

## Configure the binlog event filter

In the task configuration file, add the following configuration:

```yaml
filters:
  rule-1:
    schema-pattern: "test_*"
    ​table-pattern: "t_*"
    ​events: ["truncate table", "drop table"]
    sql-pattern: ["^DROP\\s+PROCEDURE", "^CREATE\\s+PROCEDURE"]
    ​action: Ignore
```

Starting from DM v2.0.2, you can configure the binlog event filter in the source configuration file. For details, see [Upstream Database Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file).

When you use the wildcard for matching schemas and tables, note the following:

- `schema-pattern` and `table-pattern` only support wildcards, including `*`, `?`, and `[]`. There can only be one `*` symbol in a wildcard match, and it must be at the end. For example, in `table-pattern: "t_*"`, `"t_*"` indicates all tables starting with `t_`. See [wildcard matching](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) for details.

- `sql-pattern` only supports regular expressions.
## Parameter descriptions

- [`schema-pattern`/`table-pattern`](https://docs.pingcap.com/tidb/stable/dm/table-selector): the binlog events or DDL SQL statements of upstream MySQL or MariaDB instance tables that match `schema-pattern`/`table-pattern` are filtered by the rules below.

- `events`: the binlog event array. You can only select one or more `Event`s from the following table:

    | Events            | Type | Description                   |
    | ---------------   | ---- | ----------------------------- |
    | `all`             |      | Includes all the events below |
    | `all dml`         |      | Includes all DML events below |
    | `all ddl`         |      | Includes all DDL events below |
    | `incompatible ddl changes` |      | Includes all incompatible DDL events, where "incompatible DDL" means DDL operations that might cause data loss   |
    | `none`            |      | Includes none of the events below |
    | `none ddl`        |      | Includes none of the DDL events below |
    | `none dml`        |      | Includes none of the DML events below |
    | `insert`          | DML  | The `INSERT` DML event              |
    | `update`          | DML  | The `UPDATE` DML event              |
    | `delete`          | DML  | The `DELETE` DML event              |
    | `create database` | DDL  | The `CREATE DATABASE` DDL event         |
    | `drop database`   | incompatible DDL  | The `DROP DATABASE` DDL event           |
    | `create table`    | DDL  | The `CREATE TABLE` DDL event      |
    | `create index`    | DDL  | The `CREATE INDEX` DDL event          |
    | `drop table`      | incompatible DDL  | The `DROP TABLE` DDL event              |
    | `truncate table`  | incompatible DDL  | The `TRUNCATE TABLE` DDL event          |
    | `rename table`    | incompatible DDL  | The `RENAME TABLE` DDL event            |
    | `drop index`      | incompatible DDL  | The `DROP INDEX` DDL event           |
    | `alter table`     | DDL  | The `ALTER TABLE` DDL event           |
    | `value range decrease` | incompatible DDL  | A DDL statement that decreases the value range of a column field, such as the `ALTER TABLE MODIFY COLUMN` statement that changes `VARCHAR(20)` to `VARCHAR(10)`  |
    | `precision decrease` | incompatible DDL  | A DDL statement that decreases the precision of a column field, such as the `ALTER TABLE MODIFY COLUMN` statement that changes `Decimal(10, 2)` to `Decimal(10, 1)`  |
    | `modify column` | incompatible DDL  | A DDL statement that changes the type of a column field, such as the `ALTER TABLE MODIFY COLUMN` statement that changes `INT` to `VARCHAR` |
    | `rename column` | incompatible DDL  | A DDL statement that changes the name of a column, such as the `ALTER TABLE RENAME COLUMN` statement |
    | `rename index` | incompatible DDL  | A DDL statement that changes the index name, such as the `ALTER TABLE RENAME INDEX` statement |
    | `drop column` | incompatible DDL  | A DDL statement that drops a column from a table, such as the `ALTER TABLE DROP COLUMN` statement |
    | `drop index` | incompatible DDL  | A DDL statement that drops an index in a table, such as the `ALTER TABLE DROP INDEX` statement |
    | `truncate table partition` | incompatible DDL  | A DDL statement that removes all data from a specified partition, such as the `ALTER TABLE TRUNCATE PARTITION` statement |
    | `drop primary key` | incompatible DDL  | A DDL statement that drops the primary key, such as the `ALTER TABLE DROP PRIMARY KEY` statement |
    | `drop unique key` | incompatible DDL  | A DDL statement that drops a unique key, such as the `ALTER TABLE DROP UNIQUE KEY` statement |
    | `modify default value` | incompatible DDL  | A DDL statement that modifies a column's default value, such as the `ALTER TABLE CHANGE DEFAULT` statement |
    | `modify constraint` | incompatible DDL  | A DDL statement that modifies the constraint, such as the `ALTER TABLE ADD CONSTRAINT` statement |
    | `modify columns order` | incompatible DDL  | A DDL statement that modifies the order of the columns, such as the `ALTER TABLE CHANGE AFTER` statement |
    | `modify charset` | incompatible DDL  | A DDL statement that modifies the charset of a column, such as the `ALTER TABLE MODIFY CHARSET` statement |
    | `modify collation` | incompatible DDL  | A DDL statement that modifies a column collation, such as the `ALTER TABLE MODIFY COLLATE` statement |
    | `remove auto increment` | incompatible DDL  | A DDL statement that removes an auto-incremental key |
    | `modify storage engine` | incompatible DDL  | A DDL statement that modifies the table storage engine, such as the `ALTER TABLE ENGINE = MyISAM` statement |
    | `reorganize table partition` | incompatible DDL  | A DDL statement that reorganizes partitions in a table, such as the `ALTER TABLE REORGANIZE PARTITION` statement |
    | `rebuild table partition` | incompatible DDL  | A DDL statement that rebuilds the table partition, such as the `ALTER TABLE REBUILD PARTITION` statement |
    | `exchange table partition` | incompatible DDL  | A DDL statement that exchanges a partition between two tables, such as the `ALTER TABLE EXCHANGE PARTITION` statement |
    | `coalesce table partition` | incompatible DDL  | A DDL statement that decreases the number of partitions in a table, such as the `ALTER COALESCE PARTITION` statement |

- `sql-pattern`: it is used to filter specified DDL SQL statements. The matching rule supports using a regular expression. For example, `"^DROP\\s+PROCEDURE"`.

- `action`: the string (`Do`/`Ignore`/`Error`). Based on the rules, it judges as follows:

    - `Do`: the allow list. The binlog is filtered in either of the following two conditions:
        - The type of the event is not in the `event` list of the rule.
        - The SQL statement of the event cannot be matched by `sql-pattern` of the rule.
    - `Ignore`: the block list. The binlog is filtered in either of the following two conditions:
        - The type of the event is in the `event` list of the rule.
        - The SQL statement of the event can be matched by `sql-pattern` of the rule.
    - `Error`: the error list. The binlog reports an error in either of the following two conditions:
        - The type of the event is in the `event` list of the rule.
        - The SQL statement of the event can be matched by `sql-pattern` of the rule.
    - When multiple rules match the same table, the rules are applied sequentially. The block list has a higher priority than the error list, and the error list has a higher priority than the allow list. For example:
        - If both the `Ignore` and `Error` rules are applied to the same table, the `Ignore` rule takes effect.
        - If both the `Error` and `Do` rules are applied to the same table, the `Error` rule takes effect.
