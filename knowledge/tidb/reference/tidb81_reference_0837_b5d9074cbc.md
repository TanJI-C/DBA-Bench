# SQL compatibility, statement types, and SQL mode

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/sql-concepts.md`
- Source Title: `SQL`
- Source Heading Path: `SQL | SQL > SQL statements | SQL > SQL mode`
- Source Line Ranges: `5-35`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `mysql-compatibility`, `sql-statements`, `ddl`, `dml`, `dql`, `dcl`, `sql-mode`, `syntax`, `data-validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0837_b5d9074cbc`
- Source ID: `tidb-docs-8.1:tidb-cloud/sql-concepts.md#sql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2fdfcb24d6135bd695039a1d27bc7868bfe2397a47b0d2b78ed46ba7a44445a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/sql-concepts#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/sql-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB Cloud SQL compatibility with MySQL, the meaning of DDL/DML/DQL/DCL, or what SQL mode controls.
- Retrieval Keywords: MySQL 5.7 compatibility, MySQL 8.0 compatibility, MySQL protocol, SQL statements, DDL, DML, DQL, DCL, SQL Statement Overview, SQL mode, data validation check, MySQL client, PHPMyAdmin, Navicat, MySQL Workbench, DBeaver, MySQL Compatibility
- Follow-up Guidance: The source points to MySQL Compatibility, SQL Statement Overview, and SQL Mode for more detailed statement support and mode behavior.
- Classification Note: This is reference content because it defines SQL statement categories, compatibility scope, and SQL mode behavior without providing a step-by-step procedure.

## Official Source Content

# SQL

TiDB is highly compatible with the MySQL protocol and the common features and syntax of MySQL 5.7 and MySQL 8.0. The ecosystem tools for MySQL (PHPMyAdmin, Navicat, MySQL Workbench, DBeaver and [more](https://docs.pingcap.com/tidb/v7.2/dev-guide-third-party-support#gui)) and the MySQL client can be used for TiDB.

However, some features of MySQL are not supported in TiDB. This could be because there is now a better way to solve the problem (such as the use of JSON instead of XML functions) or a lack of current demand versus effort required (such as stored procedures and functions). Additionally, some features might be difficult to implement in a distributed system. For more information, see [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility).
## SQL statements

A SQL statement is a command or instruction in SQL (Structured Query Language) composed of identifiers, parameters, variables, data types, and reserved SQL keywords. It directs the database to perform specific actions, such as retrieving, modifying, or managing data and database structures.

TiDB uses SQL statements that aim to follow ISO/IEC SQL standards, with extensions for MySQL and TiDB-specific statements where necessary.

SQL is divided into the following 4 types according to their functions:

- DDL (Data Definition Language): It is used to define database objects, including databases, tables, views, and indexes. For DDL statements in TiDB, see [Schema management / Data definition statements (DDL)](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#schema-management--data-definition-statements-ddl).

- DML (Data Manipulation Language): It is used to manipulate application-related records. For DML statements in TiDB, see [Data manipulation statements (DML)](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#data-manipulation-statements-dml).

- DQL (Data Query Language): It is used to query the records after conditional filtering.

- DCL (Data Control Language): It is used to define access privileges and security levels.

To get an overview of SQL statements in TiDB, see [SQL Statement Overview](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview).
## SQL mode

TiDB servers operate in different SQL modes and apply these modes differently for different clients. SQL mode defines the SQL syntax that TiDB supports and the type of data validation check to perform.

For more information, see [SQL Mode](https://docs.pingcap.com/tidb/stable/sql-mode).
