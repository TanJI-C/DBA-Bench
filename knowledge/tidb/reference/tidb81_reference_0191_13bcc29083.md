# TiDB CRUD SQL overview and basic DML/DQL usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-tidb-crud-sql.md`
- Source Title: `CRUD SQL in TiDB`
- Source Heading Path: `CRUD SQL in TiDB | CRUD SQL in TiDB > Before you start | CRUD SQL in TiDB > Explore SQL with TiDB | CRUD SQL in TiDB > Category | CRUD SQL in TiDB > Data Manipulation Language | CRUD SQL in TiDB > Data Query Language | CRUD SQL in TiDB > Need help?`
- Source Line Ranges: `5-117`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `crud`, `sql`, `dml`, `dql`, `insert`, `update`, `delete`, `select`, `mysql-compatibility`, `getting-started`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0191_13bcc29083`
- Source ID: `tidb-docs-8.1:develop/dev-guide-tidb-crud-sql.md#crud-sql-in-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `46bf85ad297c23233cb082f1f3932c035412ffc4de83f7df3a1894a0b3825811`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-tidb-crud-sql#crud-sql-in-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-tidb-crud-sql.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs a basic TiDB CRUD SQL reference covering DML and DQL statements, SQL categories, or MySQL-compatible query examples.
- Retrieval Keywords: CRUD SQL in TiDB, DML, DQL, DDL, DCL, MySQL compatibility, unsupported features, INSERT INTO person VALUES(1,'tom','20170912'), INSERT INTO person(id,name) VALUES('2','bob'), UPDATE person SET birthday='20180808' WHERE id=2, DELETE FROM person WHERE id=2, UPDATE and DELETE without WHERE operate on the entire table, SELECT * FROM person, SELECT name FROM person, SELECT * FROM person WHERE id < 5, SQL Statement Overview, Explore SQL with TiDB, TiDB Playground
- Follow-up Guidance: For more details, the source points to Explore SQL with TiDB, SQL Statement Overview, Compatibility with MySQL unsupported features, TiDB Playground, and the support channels on Discord, Slack, or support tickets.
- Classification Note: This is reference content because it introduces basic TiDB SQL categories and shows example CRUD statements for INSERT, UPDATE, DELETE, and SELECT.

## Official Source Content

# CRUD SQL in TiDB

This document briefly introduces how to use TiDB's CRUD SQL.
## Before you start

Please make sure you are connected to a TiDB cluster. If not, refer to [Build a {{{ .starter }}} Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud#step-1-create-a-tidb-cloud-cluster) to create a {{{ .starter }}} cluster.
## Explore SQL with TiDB

> **Note:**
>
> This document references and simplifies [Explore SQL with TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations). For more details, see [Explore SQL with TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations).

TiDB is compatible with MySQL, you can use MySQL statements directly in most cases. For unsupported features, see [Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility#unsupported-features).

To experiment with SQL and test out TiDB compatibility with MySQL queries, you can try [TiDB Playground](https://play.tidbcloud.com/?utm_source=docs&utm_medium=basic-sql-operations). You can also first deploy a TiDB cluster and then run SQL statements in it.

This page walks you through the basic TiDB SQL statements such as DDL, DML, and CRUD operations. For a complete list of TiDB statements, see [SQL Statement Overview](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview).
## Category

SQL is divided into the following 4 types according to their functions:

- **DDL (Data Definition Language)**: It is used to define database objects, including databases, tables, views, and indexes.

- **DML (Data Manipulation Language)**: It is used to manipulate application related records.

- **DQL (Data Query Language)**: It is used to query the records after conditional filtering.

- **DCL (Data Control Language)**: It is used to define access privileges and security levels.

The following mainly introduces DML and DQL. For more information about DDL and DCL, see [Explore SQL with TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations) or [SQL Statement Overview](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview).
## Data Manipulation Language

Common DML features are adding, modifying, and deleting table records. The corresponding commands are `INSERT`, `UPDATE`, and `DELETE`.

To insert data into a table, use the `INSERT` statement:

```sql
INSERT INTO person VALUES(1,'tom','20170912');
```

To insert a record containing data of some fields into a table, use the `INSERT` statement:

```sql
INSERT INTO person(id,name) VALUES('2','bob');
```

To update some fields of a record in a table, use the `UPDATE` statement:

```sql
UPDATE person SET birthday='20180808' WHERE id=2;
```

To delete the data in a table, use the `DELETE` statement:

```sql
DELETE FROM person WHERE id=2;
```

> **Note:**
>
> The `UPDATE` and `DELETE` statements without the `WHERE` clause as a filter operate on the entire table.
## Data Query Language

DQL is used to retrieve the desired data rows from a table or multiple tables.

To view the data in a table, use the `SELECT` statement:

```sql
SELECT * FROM person;
```

To query a specific column, add the column name after the `SELECT` keyword:

```sql
SELECT name FROM person;
```

The result is as follows:

```
+------+
| name |
+------+
| tom  |
+------+
1 rows in set (0.00 sec)
```

Use the `WHERE` clause to filter all records that match the conditions and then return the result:

```sql
SELECT * FROM person WHERE id < 5;
```
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
