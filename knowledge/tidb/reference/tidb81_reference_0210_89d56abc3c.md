# TiDB views usage: create, query, update, inspect, and drop

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-use-views.md`
- Source Title: `Views`
- Source Heading Path: `Views | Views > Overview | Views > Create a view | Views > Query views | Views > Update views | Views > Get view related information | Views > Get view related information > Using the `SHOW CREATE TABLE|VIEW view_name` statement | Views > Get view related information > Query the `INFORMATION_SCHEMA.VIEWS` table | Views > Drop views | Views > Limitation | Views > Read More | Views > Need help?`
- Source Line Ranges: `5-138`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `views`, `create-view`, `querying`, `replace-view`, `show-create-view`, `information-schema`, `drop-view`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0210_89d56abc3c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-use-views.md#views`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8c943cb6b8301ec2f0fd363742d894fed12f6c01eb5f431a98d09a78fb3369c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-views#views
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-use-views.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB view basics such as how to create, query, replace, inspect, or drop a view and the stated limitation around ALTER VIEW support.
- Retrieval Keywords: Views, CREATE VIEW view_name AS query, SELECT * FROM book_with_ratings LIMIT 10, CREATE OR REPLACE VIEW, DROP VIEW view_name, SHOW CREATE VIEW book_with_ratings, SHOW CREATE TABLE|VIEW view_name, INFORMATION_SCHEMA.VIEWS, information_schema.views, ALTER VIEW view_name AS query, book_with_ratings
- Follow-up Guidance: It also points to related references for Views, CREATE VIEW Statement, DROP VIEW Statement, and EXPLAIN Statements Using Views.
- Classification Note: This is reference content because it summarizes supported view operations, example SQL statements, inspection commands, and the documented limitation that ALTER VIEW is not supported.

## Official Source Content

# Views

This document describes how to use views in TiDB.
## Overview

TiDB supports views. A view acts as a virtual table, whose schema is defined by the `SELECT` statement that creates the view.

- You can create views to expose only safe fields and data to users, which ensures the security of sensitive fields and data in the underlying tables.
- You can create views for complex queries that are frequently used to make complex queries easier and more convenient.
## Create a view

In TiDB, a complex query can be defined as a view with the `CREATE VIEW` statement. The syntax is as follows:

```sql
CREATE VIEW view_name AS query;
```

Note that you cannot create a view with the same name as an existing view or table.

For example, the [multi-table join query](https://docs.pingcap.com/tidb/stable/develop/dev-guide-join-tables) gets a list of books with average ratings by joining the `books` table and the `ratings` table through a `JOIN` statement.

For the convenience of subsequent queries, you can define the query as a view using the following statement:

```sql
CREATE VIEW book_with_ratings AS
SELECT b.id AS book_id, ANY_VALUE(b.title) AS book_title, AVG(r.score) AS average_score
FROM books b
LEFT JOIN ratings r ON b.id = r.book_id
GROUP BY b.id;
```
## Query views

Once a view is created, you can use the `SELECT` statement to query the view just like a normal table.

```sql
SELECT * FROM book_with_ratings LIMIT 10;
```

When TiDB queries a view, it queries the `SELECT` statement associated with the view.
## Update views

Currently, the view in TiDB does not support the `ALTER VIEW view_name AS query;`, you can "update" a view in the following two ways:

- Delete the old view with the `DROP VIEW view_name;` statement, and then update the view by creating a new view with the `CREATE VIEW view_name AS query;` statement.
- Use the `CREATE OR REPLACE VIEW view_name AS query;` statement to overwrite an existing view with the same name.

```sql
CREATE OR REPLACE VIEW book_with_ratings AS
SELECT b.id AS book_id, ANY_VALUE(b.title), ANY_VALUE(b.published_at) AS book_title, AVG(r.score) AS average_score
FROM books b
LEFT JOIN ratings r ON b.id = r.book_id
GROUP BY b.id;
```
## Get view related information
### Using the `SHOW CREATE TABLE|VIEW view_name` statement

```sql
SHOW CREATE VIEW book_with_ratings\G
```

The result is as follows:

```
*************************** 1. row ***************************
                View: book_with_ratings
         Create View: CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `book_with_ratings` (`book_id`, `ANY_VALUE(b.title)`, `book_title`, `average_score`) AS SELECT `b`.`id` AS `book_id`,ANY_VALUE(`b`.`title`) AS `ANY_VALUE(b.title)`,ANY_VALUE(`b`.`published_at`) AS `book_title`,AVG(`r`.`score`) AS `average_score` FROM `bookshop`.`books` AS `b` LEFT JOIN `bookshop`.`ratings` AS `r` ON `b`.`id`=`r`.`book_id` GROUP BY `b`.`id`
character_set_client: utf8mb4
collation_connection: utf8mb4_general_ci
1 row in set (0.00 sec)
```
### Query the `INFORMATION_SCHEMA.VIEWS` table

```sql
SELECT * FROM information_schema.views WHERE TABLE_NAME = 'book_with_ratings'\G
```

The result is as follows:

```
*************************** 1. row ***************************
       TABLE_CATALOG: def
        TABLE_SCHEMA: bookshop
          TABLE_NAME: book_with_ratings
     VIEW_DEFINITION: SELECT `b`.`id` AS `book_id`,ANY_VALUE(`b`.`title`) AS `ANY_VALUE(b.title)`,ANY_VALUE(`b`.`published_at`) AS `book_title`,AVG(`r`.`score`) AS `average_score` FROM `bookshop`.`books` AS `b` LEFT JOIN `bookshop`.`ratings` AS `r` ON `b`.`id`=`r`.`book_id` GROUP BY `b`.`id`
        CHECK_OPTION: CASCADED
        IS_UPDATABLE: NO
             DEFINER: root@%
       SECURITY_TYPE: DEFINER
CHARACTER_SET_CLIENT: utf8mb4
COLLATION_CONNECTION: utf8mb4_general_ci
1 row in set (0.00 sec)
```
## Drop views

Use the `DROP VIEW view_name;` statement to drop a view.

```sql
DROP VIEW book_with_ratings;
```
## Limitation

For limitations of views in TiDB, see [Limitations of Views](https://docs.pingcap.com/tidb/stable/views#limitations).
## Read More

- [Views](https://docs.pingcap.com/tidb/stable/views)
- [CREATE VIEW Statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-view)
- [DROP VIEW Statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-view)
- [EXPLAIN Statements Using Views](https://docs.pingcap.com/tidb/stable/explain-views)
- [TiFlink: Strongly Consistent Materialized Views Using TiKV and Flink](https://github.com/tiflink/tiflink)
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
