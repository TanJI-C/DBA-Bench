# Database, table, column, and data type concepts

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/database-schema-concepts.md`
- Source Title: `Database Schema`
- Source Heading Path: `Database Schema | Database Schema > Databases | Database Schema > Databases > System databases | Database Schema > Databases > `test` database | Database Schema > Tables | Database Schema > Tables > System table | Database Schema > Tables > Cached table | Database Schema > Tables > Temporary table | Database Schema > Tables > Partitioned table | Database Schema > Columns | Database Schema > Generated columns | Database Schema > Data types`
- Source Line Ranges: `5-75`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`, `tidb`, `tikv`
- Topic Tags: `schema`, `databases`, `system-databases`, `tables`, `system-tables`, `cached-tables`, `temporary-tables`, `partitioning`, `columns`, `generated-columns`, `data-types`, `json`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0797_f3fe6977b7`
- Source ID: `tidb-docs-8.1:tidb-cloud/database-schema-concepts.md#database-schema`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `251a79e506db89bedab530bea00ee5dbc2e9b067fa4fb67eea137936451b6a3e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/database-schema-concepts#database-schema
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/database-schema-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of TiDB database schema concepts in TiDB Cloud, including system databases, table types, columns, generated columns, and supported data types.
- Retrieval Keywords: Database Schema, system databases, INFORMATION_SCHEMA, mysql schema, performance_schema, sys, test database, system table, cached table, temporary table, partitioned table, generated columns, virtual generated column, stored generated column, JSON data type, SPATIAL type
- Follow-up Guidance: It also points to related topics such as constraints, cached tables, partitioned tables, generated columns, and MySQL-compatible data types.
- Classification Note: This is reference content because it defines schema objects and features such as databases, tables, columns, generated columns, and data types without giving a procedural workflow.

## Official Source Content

# Database Schema

A database schema defines the structure and organization of data within databases, tables, columns, indexes, and other objects.

This document introduces the key concepts of database schemas, such as databases, tables, columns, data types, constraints, and indexes. It also introduces advanced features such as temporary tables for managing intermediate data seamlessly, vector indexes for efficient approximate nearest neighbor (ANN) searches, and cached tables to improve read performance.
## Databases

A database in TiDB is a collection of objects such as tables and indexes.
### System databases

System databases are default databases created by TiDB to store system tables. TiDB provides the following system databases:

- [`INFORMATION_SCHEMA`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema)

- [`mysql`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema)

- [`performance_schema`](https://docs.pingcap.com/tidb/stable/performance-schema/performance-schema)

- [`sys`](https://docs.pingcap.com/tidb/stable/sys-schema/sys-schema)
### `test` database

TiDB comes with a default database named `test`. However, it is recommended that you create your own database instead of using the `test` database.
## Tables

A table is a collection of related data in a [database](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview#database).

Each table consists of rows and columns. Each value in a row belongs to a specific column. Each column allows only a single data type. To further qualify columns, you can add some [constraints](https://docs.pingcap.com/tidb/stable/constraints). To accelerate calculations, you can add [generated columns](https://docs.pingcap.com/tidb/stable/generated-columns).
### System table

- The `mysql` schema contains TiDB system tables. The design is similar to the `mysql` schema in MySQL, where tables such as `mysql.user` can be edited directly. It also contains a number of tables that are extensions to MySQL.

- Information Schema provides an ANSI-standard way of viewing system metadata. TiDB also provides a number of custom `INFORMATION_SCHEMA` tables, in addition to the tables included for MySQL compatibility. Many `INFORMATION_SCHEMA` tables have a corresponding `SHOW` command. The benefit of querying `INFORMATION_SCHEMA` is that it is possible to join between tables.

- Performance Schema. TiDB implements performance schema tables for MySQL compatibility.
### Cached table

TiDB introduces the [cached table](https://docs.pingcap.com/tidb/stable/cached-tables) feature for frequently accessed but rarely updated small hotspot tables. When this feature is used, the data of an entire table is loaded into the memory of the TiDB server, and TiDB directly gets the table data from the memory without accessing TiKV, which improves the read performance.
### Temporary table

The temporary tables feature solves the issue of temporarily storing the intermediate results of an application, which frees you from frequently creating and dropping tables. You can store the intermediate calculation data in temporary tables. When the intermediate data is no longer needed, TiDB automatically cleans up and recycles the temporary tables. This avoids user applications being too complicated, reduces table management overhead, and improves performance.
### Partitioned table

In TiDB, [partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table) enables you to divide a large table into one or more manageable pieces called partitions. Each partition is independent and can be managed individually.
## Columns

A column is subordinate to a table. Each table has at least one column. Columns provide a structure to a table by dividing the values in each row into small cells of a single data type.

For more information, see [Define columns](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#define-columns).
## Generated columns

TiDB lets you extract data from the JSON data type as a [generated column](https://docs.pingcap.com/tidb/stable/generated-columns).

Unlike general columns, the value of the generated column is calculated by the expression in the column definition. When inserting or updating a generated column, you cannot assign a value, but only use `DEFAULT`.

There are two kinds of generated columns: virtual and stored. A virtual generated column occupies no storage and is computed when it is read. A stored generated column is computed when it is written (inserted or updated) and occupies storage. Compared with the virtual generated columns, the stored generated columns have better read performance, but take up more disk space.
## Data types

TiDB supports all the data types in MySQL except the `SPATIAL` type. This includes all the [numeric types](https://docs.pingcap.com/tidb/stable/data-type-numeric), [string types](https://docs.pingcap.com/tidb/stable/data-type-string), [date & time types](https://docs.pingcap.com/tidb/stable/data-type-date-and-time), and [the JSON type](https://docs.pingcap.com/tidb/stable/data-type-json).
