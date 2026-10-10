# Information Schema table catalogs and TiDB extension scope note

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema.md`
- Source Title: `Information Schema`
- Source Heading Path: `Information Schema > Tables for MySQL compatibility | Information Schema > Tables that are TiDB extensions`
- Source Line Ranges: `59-106`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `information_schema`, `system-metadata`, `mysql-compatibility`, `system-tables`, `tidb-extensions`, `cloud-support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0435_c1c912eb3c`
- Source ID: `tidb-docs-8.1:information-schema/information-schema.md#tables-for-mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `45b73a4ca4209281a4b0ab5108bdabed6d41d494fbe115aa85040cf05c73b4f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema#tables-for-mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which INFORMATION_SCHEMA tables in TiDB are available for MySQL compatibility metadata, which ones are TiDB-specific extensions, or which listed tables are not implemented and return zero rows.
- Retrieval Keywords: INFORMATION_SCHEMA, Tables for MySQL compatibility, Tables that are TiDB extensions, CHARACTER_SETS, CHECK_CONSTRAINTS, COLLATIONS, COLLATION_CHARACTER_SET_APPLICABILITY, COLUMNS, ENGINES, KEY_COLUMN_USAGE, PARTITIONS, PROCESSLIST, SCHEMATA, SESSION_VARIABLES, STATISTICS, TABLES, TABLE_CONSTRAINTS, USER_ATTRIBUTES, USER_PRIVILEGES, VARIABLES_INFO, VIEWS, COLUMN_PRIVILEGES not implemented, COLUMN_STATISTICS not implemented, EVENTS not implemented, FILES not implemented, GLOBAL_STATUS not implemented, GLOBAL_VARIABLES not implemented, OPTIMIZER_TRACE not implemented, PARAMETERS not implemented, PLUGINS not implemented, PROFILING not implemented, ROUTINES not implemented, SCHEMA_PRIVILEGES not implemented, SESSION_STATUS not implemented, TABLESPACES not implemented, TABLE_PRIVILEGES not implemented, TRIGGERS not implemented, returns zero rows, TiDB Cloud system tables unsupported
- Follow-up Guidance: The note says some TiDB extension tables are only supported on TiDB Self-Managed and not supported on TiDB Cloud, and points to the TiDB Cloud System tables list for unsupported tables.
- Classification Note: This is reference content because it is a catalog of INFORMATION_SCHEMA table names, descriptions, implementation status, and a scope note about TiDB extension support.

## Official Source Content

| Table name                                                                              | Description                 |
|-----------------------------------------------------------------------------------------|-----------------------------|
| [`CHARACTER_SETS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-character-sets)            | Provides a list of character sets the server supports. |
| [`CHECK_CONSTRAINTS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-check-constraints)            | Provides information about [`CHECK` constraints](https://docs.pingcap.com/tidb/stable/constraints#check) on tables. |
| [`COLLATIONS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collations)                    | Provides a list of collations that the server supports. |
| [`COLLATION_CHARACTER_SET_APPLICABILITY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collation-character-set-applicability) | Explains which collations apply to which character sets. |
| [`COLUMNS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-columns)                          | Provides a list of columns for all tables. |
| `COLUMN_PRIVILEGES`                                                                     | Not implemented by TiDB. Returns zero rows. |
| `COLUMN_STATISTICS`                                                                     | Not implemented by TiDB. Returns zero rows. |
| [`ENGINES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-engines)                          | Provides a list of supported storage engines. |
| `EVENTS`                                                                                | Not implemented by TiDB. Returns zero rows. |
| `FILES`                                                                                 | Not implemented by TiDB. Returns zero rows. |
| `GLOBAL_STATUS`                                                                         | Not implemented by TiDB. Returns zero rows. |
| `GLOBAL_VARIABLES`                                                                      | Not implemented by TiDB. Returns zero rows. |
| [`KEY_COLUMN_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-key-column-usage)        | Describes the key constraints of the columns, such as the primary key constraint. |
| `OPTIMIZER_TRACE`                                                                       | Not implemented by TiDB. Returns zero rows. |
| `PARAMETERS`                                                                            | Not implemented by TiDB. Returns zero rows. |
| [`PARTITIONS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-partitions)                    | Provides a list of table partitions. |
| `PLUGINS`                                                                               | Not implemented by TiDB. Returns zero rows. |
| [`PROCESSLIST`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-processlist)                  | Provides similar information to the command `SHOW PROCESSLIST`. |
| `PROFILING`                                                                             | Not implemented by TiDB. Returns zero rows. |
| `REFERENTIAL_CONSTRAINTS`                                                               | Provides information on `FOREIGN KEY` constraints. |
| `ROUTINES`                                                                              | Not implemented by TiDB. Returns zero rows. |
| [`SCHEMATA`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-schemata)                        | Provides similar information to `SHOW DATABASES`. |
| `SCHEMA_PRIVILEGES`                                                                     | Not implemented by TiDB. Returns zero rows. |
| `SESSION_STATUS`                                                                        | Not implemented by TiDB. Returns zero rows. |
| [`SESSION_VARIABLES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-session-variables)      | Provides similar functionality to the command `SHOW SESSION VARIABLES` |
| [`STATISTICS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-statistics)                    | Provides information on table indexes. |
| [`TABLES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tables)                            | Provides a list of tables that the current user has visibility of. Similar to `SHOW TABLES`. |
| `TABLESPACES`                                                                           | Not implemented by TiDB. Returns zero rows. |
| [`TABLE_CONSTRAINTS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-table-constraints)      | Provides information on primary keys, unique indexes and foreign keys. |
| `TABLE_PRIVILEGES`                                                                      | Not implemented by TiDB. Returns zero rows. |
| `TRIGGERS`                                                                              | Not implemented by TiDB. Returns zero rows. |
| [`USER_ATTRIBUTES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-user-attributes) | Summarizes information about user comments and user attributes. |
| [`USER_PRIVILEGES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-user-privileges)          | Summarizes the privileges associated with the current user. |
| [`VARIABLES_INFO`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-variables-info)            | Provides information about TiDB system variables. |
| [`VIEWS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-views)                              | Provides a list of views that the current user has visibility of. Similar to running `SHOW FULL TABLES WHERE table_type = 'VIEW'` |
## Tables that are TiDB extensions

> **Note:**
>
> Some of the following tables are only supported on TiDB Self-Managed and not supported on TiDB Cloud. To get a full list of unsupported tables on TiDB Cloud, see [System tables](https://docs.pingcap.com/tidbcloud/limited-sql-features#system-tables).
