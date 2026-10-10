# Information Schema overview and MySQL compatibility tables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema.md`
- Source Title: `Information Schema`
- Source Heading Path: `Information Schema | Information Schema > Tables for MySQL compatibility`
- Source Line Ranges: `5-58`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `information_schema`, `metadata`, `mysql-compatibility`, `system-tables`, `show-statements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0434_b01a140d95`
- Source ID: `tidb-docs-8.1:information-schema/information-schema.md#information-schema`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c48d7e725bbce10443d1aa6bd85da22c31cce9dac3e423daab06cfbd7657220e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema#information-schema
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for an overview of `INFORMATION_SCHEMA` in TiDB, the MySQL compatibility tables it includes, or which metadata tables correspond to `SHOW` statements.
- Retrieval Keywords: INFORMATION_SCHEMA, Information Schema, ANSI-standard way of viewing system metadata, Tables for MySQL compatibility, SHOW statement, join between tables, CHARACTER_SETS, CHECK_CONSTRAINTS, COLLATIONS, COLLATION_CHARACTER_SET_APPLICABILITY, COLUMNS, ENGINES, KEYWORDS, KEY_COLUMN_USAGE, PARTITIONS, PROCESSLIST, SCHEMATA, SESSION_VARIABLES, STATISTICS, TABLES, TABLE_CONSTRAINTS, USER_ATTRIBUTES, USER_PRIVILEGES, VARIABLES_INFO, VIEWS, Not implemented by TiDB. Returns zero rows.
- Follow-up Guidance: If the user needs details for a specific metadata table, this source points to table-specific `INFORMATION_SCHEMA` pages such as `COLUMNS`, `TABLES`, `STATISTICS`, `PROCESSLIST`, and `VIEWS`.
- Classification Note: This is reference content because it lists `INFORMATION_SCHEMA` tables, their descriptions, and MySQL compatibility status, including tables that are not implemented and return zero rows.

## Official Source Content

# Information Schema

Information Schema provides an ANSI-standard way of viewing system metadata. TiDB also provides a number of custom `INFORMATION_SCHEMA` tables, in addition to the tables included for MySQL compatibility.

Many `INFORMATION_SCHEMA` tables have a corresponding `SHOW` statement. The benefit of querying `INFORMATION_SCHEMA` is that it is possible to join between tables.
## Tables for MySQL compatibility

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
| [`KEYWORDS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-keywords)                        | Provides a full list of keywords.                |
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
