# DM table routing usage examples and incorrect configurations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-table-routing.md`
- Source Title: `TiDB Data Migration Table Routing`
- Source Heading Path: `TiDB Data Migration Table Routing > Usage examples > Merge sharded schemas and tables | TiDB Data Migration Table Routing > Usage examples > Extract table, schema, and source information and write into the merged table | TiDB Data Migration Table Routing > Usage examples > Extract table, schema, and source information and write into the merged table > Incorrect examples of creating merged tables | TiDB Data Migration Table Routing > Usage examples > Merge sharded schemas | TiDB Data Migration Table Routing > Usage examples > Incorrect table routing`
- Source Line Ranges: `60-241`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `table-routing`, `shard-merge`, `schema-routing`, `table-routing-rules`, `extract-table`, `extract-schema`, `extract-source`, `merged-table`, `ddl-routing`, `dml-routing`, `validation`, `errors`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0083_07fc5cf9df`
- Source ID: `tidb-docs-8.1:dm/dm-table-routing.md#merge-sharded-schemas-and-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9455249e77da06862c4ee439078e4658bffd9fa0fc69c4039b07471d5c1c0adf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-table-routing#merge-sharded-schemas-and-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-table-routing.md

## Retrieval Guidance

- Use When: Use this chunk when looking for DM table routing examples for merging sharded schemas and tables, extracting shard and source information into a merged table, or understanding invalid routing and merged table definitions.
- Retrieval Keywords: Merge sharded schemas and tables, Extract table, schema, and source information and write into the merged table, Incorrect examples of creating merged tables, Merge sharded schemas, Incorrect table routing, schema test doesn't exist, c_table, c_schema, c_source, CREATE TABLE `test`.`t`, mysql-01, mysql-02, rule-1, rule-2, schema-pattern: "test_*", table-pattern: "t_*", target-schema: "test", target-table: "t", source information of sharded tables and schemas might fail to be written to the merged table
- Follow-up Guidance: The chunk includes the note that if the downstream schema `test` does not exist and only `rule-1` is configured, migration reports the `schema test doesn't exist` error.
- Classification Note: This is classified as configuration because the content provides concrete routing rule examples, required merged table definitions, and examples of invalid configurations that cause routing or write failures.

## Official Source Content

### Merge sharded schemas and tables

Assuming in the scenario of sharded schemas and tables, you want to migrate the `test_{1,2,3...}`.`t_{1,2,3...}` tables in two upstream MySQL instances to the `test`.`t` table in the downstream TiDB instance.

To migrate the upstream instances to the downstream `test`.`t`, you must create the following routing rules:

- `rule-1` is used to migrate DML or DDL statements of the table that matches `schema-pattern: "test_*"` and `table-pattern: "t_*"` to the downstream `test`.`t`.
- `rule-2` is used to migrate DDL statements of the schema that matches `schema-pattern: "test_*"`, such as `CREATE/DROP SCHEMA xx`.

> **Note:**
>
> - If the downstream `schema: test` already exists and is not to be deleted, you can omit `rule-2`.
> - If the downstream `schema: test` does not exist and only `rule-1` is configured, then it reports the `schema test doesn't exist` error during migration.

```yaml
  rule-1:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    target-schema: "test"
    target-table: "t"
  rule-2:
    schema-pattern: "test_*"
    target-schema: "test"
```
### Extract table, schema, and source information and write into the merged table

Assuming in the scenario of sharded schemas and tables, you want to migrate the `test_{1,2,3...}`.`t_{1,2,3...}` tables in two upstream MySQL instances to the `test`.`t` table in the downstream TiDB instance. At the same time, you want to extract the source information of the sharded tables and write it to the downstream merged table.

To migrate the upstream instances to the downstream `test`.`t`, you must create routing rules similar to the previous section [Merge sharded schemas and tables](#merge-sharded-schemas-and-tables). In addition, you need to add the `extract-table`, `extract-schema`, and `extract-source` configurations:

- `extract-table`: For a sharded table matching `schema-pattern` and `table-pattern`, DM extracts the sharded table name by using `table-regexp` and writes the name suffix without the `t_` part to `target-column` of the merged table, that is, the `c_table` column.
- `extract-schema`: For a sharded schema matching `schema-pattern` and `table-pattern`, DM extracts the sharded schema name by using `schema-regexp` and writes the name suffix without the `test_` part to `target-column` of the merged table, that is, the `c_schema` column.
- `extract-source`: For a sharded table matching `schema-pattern` and `table-pattern`, DM writes the source instance information to the `target-column` of the merged table, that is, the `c_source` column.

```yaml
  rule-1:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    target-schema: "test"
    target-table: "t"
    extract-table:
      table-regexp: "t_(.*)"
      target-column: "c_table"
    extract-schema:
      schema-regexp: "test_(.*)"
      target-column: "c_schema"
    extract-source:
      source-regexp: "(.*)"
      target-column: "c_source"
  rule-2:
    schema-pattern: "test_*"
    target-schema: "test"
```

To extract the source information of upstream sharded tables to the merged table in the downstream, you **must manually create a merged table in the downstream before starting the migration**. The merged table must contain the three `target-columns` (`c_table`, `c_schema`, and `c_source`) used for specifying the source information. In addition, these columns **must be the last columns and be [string types](https://docs.pingcap.com/tidb/stable/data-type-string)**.

```sql
CREATE TABLE `test`.`t` (
    a int(11) PRIMARY KEY,
    c_table varchar(10) DEFAULT NULL,
    c_schema varchar(10) DEFAULT NULL,
    c_source varchar(10) DEFAULT NULL
);
```

Assume that the upstream has the following two data sources:

Data source `mysql-01`:

```sql
mysql> select * from test_11.t_1;
+---+
| a |
+---+
| 1 |
+---+
mysql> select * from test_11.t_2;
+---+
| a |
+---+
| 2 |
+---+
mysql> select * from test_12.t_1;
+---+
| a |
+---+
| 3 |
+---+
```

Data source `mysql-02`:

```sql
mysql> select * from test_13.t_3;
+---+
| a |
+---+
| 4 |
+---+
```

After migration using DM, data in the merged table will be as follows:

```sql
mysql> select * from test.t;
+---+---------+----------+----------+
| a | c_table | c_schema | c_source |
+---+---------+----------+----------+
| 1 | 1       | 11       | mysql-01 |
| 2 | 2       | 11       | mysql-01 |
| 3 | 1       | 12       | mysql-01 |
| 4 | 3       | 13       | mysql-02 |
+---+---------+----------+----------+
```
#### Incorrect examples of creating merged tables

> **Note:**
>
> If any of the following errors occur, source information of sharded tables and schemas might fail to be written to the merged table.

- `c-table` is not in the last three columns:

```sql
CREATE TABLE `test`.`t` (
    c_table varchar(10) DEFAULT NULL,
    a int(11) PRIMARY KEY,
    c_schema varchar(10) DEFAULT NULL,
    c_source varchar(10) DEFAULT NULL
);
```

- `c-source` is absent:

```sql
CREATE TABLE `test`.`t` (
    a int(11) PRIMARY KEY,
    c_table varchar(10) DEFAULT NULL,
    c_schema varchar(10) DEFAULT NULL,
);
```

- `c_schema` is not a string type:

```sql
CREATE TABLE `test`.`t` (
    a int(11) PRIMARY KEY,
    c_table varchar(10) DEFAULT NULL,
    c_schema int(11) DEFAULT NULL,
    c_source varchar(10) DEFAULT NULL,
);
```
### Merge sharded schemas

Assuming in the scenario of sharded schemas, you want to migrate the `test_{1,2,3...}`.`t_{1,2,3...}` tables in the two upstream MySQL instances to the `test`.`t_{1,2,3...}` tables in the downstream TiDB instance.

To migrate the upstream schemas to the downstream `test`.`t_[1,2,3]`, you only need to create one routing rule.

```yaml
  rule-1:
    schema-pattern: "test_*"
    target-schema: "test"
```
### Incorrect table routing

Assuming that the following two routing rules are configured and `test_1_bak`.`t_1_bak` matches both `rule-1` and `rule-2`, an error is reported because the table routing configuration violates the number limitation.

```yaml
  rule-1:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    target-schema: "test"
    target-table: "t"
  rule-2:
    schema-pattern: "test_1_bak"
    table-pattern: "t_1_bak"
    target-schema: "test"
    target-table: "t_bak"
```
