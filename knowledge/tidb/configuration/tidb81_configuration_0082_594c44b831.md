# DM table routing overview and configuration parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-table-routing.md`
- Source Title: `TiDB Data Migration Table Routing`
- Source Heading Path: `TiDB Data Migration Table Routing | TiDB Data Migration Table Routing > Configure table routing | TiDB Data Migration Table Routing > Parameter descriptions | TiDB Data Migration Table Routing > Usage examples`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `table-routing`, `schema-pattern`, `table-pattern`, `wildcards`, `regular-expressions`, `target-schema`, `target-table`, `extract-table`, `extract-schema`, `extract-source`, `shard-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0082_594c44b831`
- Source ID: `tidb-docs-8.1:dm/dm-table-routing.md#tidb-data-migration-table-routing`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c292156b8b39704ae8eadaa29b71164f74714c594f384d6455b327ce71fb499`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-table-routing#tidb-data-migration-table-routing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-table-routing.md

## Retrieval Guidance

- Use When: Use this chunk when looking for DM table routing syntax, supported matching forms, or parameter meanings for mapping upstream MySQL or MariaDB schemas and tables to downstream target-schema and target-table.
- Retrieval Keywords: TiDB Data Migration Table Routing, Configure table routing, schema-pattern, table-pattern, target-schema, target-table, extract-table, extract-schema, extract-source, table-regexp, schema-regexp, source-regexp, target-column, wildcards, regular expressions, rule-1, rule-2, CREATE/DROP SCHEMA xx, Table selector, sharded tables, merged table
- Follow-up Guidance: It also points to usage examples for four scenarios and references the tutorial for migrating and merging MySQL shards of small datasets to TiDB.
- Classification Note: This is classified as configuration because the content defines YAML routing rules, matching parameters, and extraction settings used by DM table routing.

## Official Source Content

# TiDB Data Migration Table Routing

When you migrate data using TiDB Data Migration (DM), you can configure the table routing to migrate a certain table of the upstream MySQL or MariaDB instance to the specified table in the downstream.

> **Note:**
>
> - Configuring multiple different routing rules for a single table is not supported.
> - The match rule of schema needs to be configured separately, which is used to migrate `CREATE/DROP SCHEMA xx`, as shown in `rule-2` of the [Configure table routing](#configure-table-routing) section.
## Configure table routing

```yaml
routes:
  rule-1:
    schema-pattern: "test_*"
    table-pattern: "t_*"
    target-schema: "test"
    target-table: "t"
    # extract-table, extract-schema, and extract-source are optional and
    # are required only when you need to extract information about sharded
    # tables, sharded schemas, and source datatabase information.
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

Regular expressions and wildcards are supported to match database and table names. In simple scenarios, it is recommended that you use the wildcard for matching schemas and tables. However, note the following:

- Wildcards including `*`, `?`, and `[]` are supported. There can only be one `*` symbol in a wildcard match, and it must be at the end. For example, in `table-pattern: "t_*"`, `"t_*"` indicates all tables starting with `t_`. See [wildcard matching](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) for details.

- `table-regexp`, `schema-regexp`, and `source-regexp` only support regular expressions and cannot start with the `~` symbol.

- `schema-pattern` and `table-pattern` support both wildcards and regular expressions. Regular expressions must begin with the `~` symbol.
## Parameter descriptions

- DM migrates the upstream MySQL or MariaDB instance tables that match the [`schema-pattern`/`table-pattern` rule provided by Table selector](https://docs.pingcap.com/tidb/stable/dm/table-selector) to the downstream `target-schema`/`target-table`.
- For sharded tables that match the `schema-pattern`/`table-pattern` rules, DM extracts the table name by using the `extract-table`.`table-regexp` regular expression, the schema name by using the `extract-schema`.`schema-regexp` regular expression, and source information by using the `extract-source`.`source-regexp` regular expression. Then DM writes the extracted information to the corresponding `target-column` in the merged table in the downstream.
## Usage examples

This section shows the usage examples in four different scenarios.

If you need to migrate and merge MySQL shards of small datasets to TiDB, refer to [this tutorial](https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb).
