# TiDB schema objects and index basics

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-schema-design-overview.md`
- Source Title: `TiDB Database Schema Design Overview`
- Source Heading Path: `TiDB Database Schema Design Overview | TiDB Database Schema Design Overview > Objects in TiDB | TiDB Database Schema Design Overview > Objects in TiDB > Database | TiDB Database Schema Design Overview > Objects in TiDB > Table | TiDB Database Schema Design Overview > Objects in TiDB > Index | TiDB Database Schema Design Overview > Objects in TiDB > Index > Specialized indexes | TiDB Database Schema Design Overview > Objects in TiDB > Other supported logical objects`
- Source Line Ranges: `5-69`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `schema-design`, `database-objects`, `tables`, `indexes`, `primary-key`, `clustered-index`, `views`, `sequences`, `temporary-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0181_ed6f527c00`
- Source ID: `tidb-docs-8.1:develop/dev-guide-schema-design-overview.md#tidb-database-schema-design-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `24a986651f60e4f7f998f80b43be0119e54965be99499faf9d08224ca2513d8a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview#tidb-database-schema-design-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-schema-design-overview.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs a TiDB schema design overview covering database, table, index, primary key, clustered index behavior, and other supported logical objects.
- Retrieval Keywords: TiDB Database Schema Design Overview, Objects in TiDB, database, table, index, Primary Key, Secondary Index, clustered index, CLUSTERED, NONCLUSTERED, CREATE TABLE, @@global.tidb_enable_clustered_index, specialized indexes, Indexing and constraints, view, sequence, temporary table, test database
- Follow-up Guidance: It points to Clustered Indexes, Indexing and constraints, constraints, generated columns, views, CREATE SEQUENCE, and temporary tables for more details.
- Classification Note: This is reference content because it defines TiDB schema objects and terminology, including how primary keys and clustered indexes are described in TiDB.

## Official Source Content

# TiDB Database Schema Design Overview

This document provides the basics of TiDB database schema design, including the objects in TiDB, access control, database schema changes, and object limitations.

In the subsequent documents, [Bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) will be taken as an example to show you how to design a database and perform data read and write operations in a database.
## Objects in TiDB

To distinguish some general terms, here is a brief agreement on the terms used in TiDB:

- To avoid confusion with the generic term [database](https://en.wikipedia.org/wiki/Database), **database** in this document refers to a logical object, **TiDB** refers to TiDB itself, and **cluster** refers to a deployed instance of TiDB.

- TiDB uses MySQL-compatible syntax, in which **schema** means the generic term [schema](https://en.wiktionary.org/wiki/schema) instead of a logical object in a database. For more information, see [MySQL documentation](https://dev.mysql.com/doc/refman/8.0/en/create-database.html). Make sure that you note this difference if you are migrating from databases that have schemas as logical objects (for example, [PostgreSQL](https://www.postgresql.org/docs/current/ddl-schemas.html), [Oracle](https://docs.oracle.com/en/database/oracle/oracle-database/21/tdddg/creating-managing-schema-objects.html), and [Microsoft SQL Server](https://docs.microsoft.com/en-us/sql/relational-databases/security/authentication-access/create-a-database-schema?view=sql-server-ver15)).
### Database

A database in TiDB is a collection of objects such as tables and indexes.

TiDB comes with a default database named `test`. However, it is recommended that you create your own database instead of using the `test` database.
### Table

A table is a collection of related data in a [database](#database).

Each table consists of **rows** and **columns**. Each value in a row belongs to a specific **column**. Each column allows only a single data type. To further qualify columns, you can add some [constraints](https://docs.pingcap.com/tidb/stable/constraints). To accelerate calculations, you can add [generated columns](https://docs.pingcap.com/tidb/stable/generated-columns).
### Index

An index is a copy of selected columns in a table. You can create an index using one or more columns of a [table](#table). With indexes, TiDB can quickly locate data without having to search every row in a table every time, which greatly improves your query performance.

There are two common types of indexes:

- **Primary Key**: indexes on the primary key column.
- **Secondary Index**: indexes on non-primary key columns.

> **Note:**
>
> In TiDB, the default definition of **Primary Key** is different from that in [InnoDB](https://dev.mysql.com/doc/refman/8.0/en/innodb-storage-engine.html) (a common storage engine of MySQL).
>
> - In InnoDB, the definition of **Primary Key** is unique, not null, and a **clustered index**.
> - In TiDB, the definition of **Primary Key** is unique and not null. But the primary key is not guaranteed to be a **clustered index**. To specify whether the primary key is a clustered index, you can add non-reserved keywords `CLUSTERED` or `NONCLUSTERED` after `PRIMARY KEY` in a `CREATE TABLE` statement. If a statement does not explicitly specify these keywords, the default behavior is controlled by the system variable `@@global.tidb_enable_clustered_index`. For more information, see [Clustered Indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes).
#### Specialized indexes

To improve query performance of various user scenarios, TiDB provides you with some specialized types of indexes. For details of each type, see [Indexing and constraints](https://docs.pingcap.com/tidb/stable/basic-features#indexing-and-constraints).

To improve query performance of various user scenarios, TiDB provides you with some specialized types of indexes. For details of each type, see [Indexing and constraints](https://docs.pingcap.com/tidb/stable/basic-features#indexing-and-constraints).
### Other supported logical objects

TiDB supports the following logical objects at the same level as **table**:

- [View](https://docs.pingcap.com/tidb/stable/views): a view acts as a virtual table, whose schema is defined by the `SELECT` statement that creates the view.
- [Sequence](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence): a sequence generates and stores sequential data.
- [Temporary table](https://docs.pingcap.com/tidb/stable/temporary-tables): a table whose data is not persistent.
