# Clustered index and column constraints in CREATE TABLE

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-table.md`
- Source Title: `Create a Table`
- Source Heading Path: `Create a Table > Clustered or not | Create a Table > Add column constraints | Create a Table > Add column constraints > Set default value | Create a Table > Add column constraints > Prevent duplicate values | Create a Table > Add column constraints > Prevent null values`
- Source Line Ranges: `134-231`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `create-table`, `clustered-index`, `primary-key`, `default-value`, `unique-constraint`, `not-null`, `column-constraints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0094_795ea2b16b`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-table.md#clustered-or-not`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4f645efb7c5804c2ebc8fc1dabcb63cd9d260b3f282dc7ff72ad990bd5205bc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#clustered-or-not
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about CREATE TABLE syntax for PRIMARY KEY CLUSTERED or NONCLUSTERED behavior, or about DEFAULT, UNIQUE, and NOT NULL column constraints in TiDB.
- Retrieval Keywords: CREATE TABLE, CLUSTERED, NONCLUSTERED, PRIMARY KEY (`book_id`,`user_id`) CLUSTERED, clustered index, non-clustered index, _tidb_rowid, DEFAULT, DEFAULT NOW(), ON UPDATE NOW(), UNIQUE, UNIQUE NOT NULL, NOT NULL, column constraints, bookshop.ratings, bookshop.users, nickname varchar(100) UNIQUE NOT NULL
- Follow-up Guidance: The content also points to related material on selecting clustered indexes, TiDB constraints, and default values of different data types.
- Classification Note: This is reference content because it explains SQL CREATE TABLE concepts and syntax examples for clustered indexes and column constraints.

## Official Source Content

## Clustered or not

TiDB supports the [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes) feature since v5.0. This feature controls how data is stored in tables containing primary keys. It provides TiDB the ability to organize tables in a way that can improve the performance of certain queries.

The term clustered in this context refers to the organization of how data is stored and not a group of database servers working together. Some database management systems refer to clustered index tables as index-organized tables (IOT).

Currently, tables **_containing primary_** keys in TiDB are divided into the following two categories:

- `NONCLUSTERED`: The primary key of the table is non-clustered index. In tables with non-clustered indexes, the keys for row data consist of internal `_tidb_rowid` implicitly assigned by TiDB. Because primary keys are essentially unique indexes, tables with non-clustered indexes need at least two key-value pairs to store a row, which are:
    - `_tidb_rowid` (key) - row data (value)
    - Primary key data (key) - `_tidb_rowid` (value)
- `CLUSTERED`: The primary key of the table is clustered index. In tables with clustered indexes, the keys for row data consist of primary key data given by the user. Therefore, tables with clustered indexes need only one key-value pair to store a row, which is:
    - Primary key data (key) - row data (value)

As described in [select primary key](#select-primary-key), **clustered indexes** are controlled in TiDB using the keywords `CLUSTERED` and `NONCLUSTERED`.

> **Note:**
>
> TiDB supports clustering only by a table's `PRIMARY KEY`. With clustered indexes enabled, the terms _the_ `PRIMARY KEY` and _the clustered index_ might be used interchangeably. `PRIMARY KEY` refers to the constraint (a logical property), and clustered index describes the physical implementation of how the data is stored.

Following the [guidelines for selecting clustered index](#guidelines-to-follow-when-selecting-clustered-index), the following example creates a table with an association between `books` and `users`, which represents the `ratings` of a `book` by `users`. The example creates the table and constructs a composite primary key using `book_id` and `user_id`, and creates a **clustered index** on that **primary key**.

```sql
CREATE TABLE `bookshop`.`ratings` (
  `book_id` bigint,
  `user_id` bigint,
  `score` tinyint,
  `rated_at` datetime,
  PRIMARY KEY (`book_id`,`user_id`) CLUSTERED
);
```
## Add column constraints

In addition to [primary key constraints](#select-primary-key), TiDB also supports other **column constraints** such as [NOT NULL](https://docs.pingcap.com/tidb/stable/constraints#not-null) constraint, [UNIQUE KEY](https://docs.pingcap.com/tidb/stable/constraints#unique-key) constraint, and `DEFAULT`. For complete constraints, refer to the [TiDB constraints](https://docs.pingcap.com/tidb/stable/constraints) document.
### Set default value

To set a default value on a column, use the `DEFAULT` constraint. The default value allows you to insert data without specifying a value for each column.

You can use `DEFAULT` together with [supported SQL functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/functions-and-operators-overview) to move the calculation of defaults out of the application layer, thus saving resources of the application layer. The resources consumed by the calculation do not disappear and are moved to the TiDB cluster. Commonly, you can insert data with the default time. The following exemplifies setting the default value in the `ratings` table:

```sql
CREATE TABLE `bookshop`.`ratings` (
  `book_id` bigint,
  `user_id` bigint,
  `score` tinyint,
  `rated_at` datetime DEFAULT NOW(),
  PRIMARY KEY (`book_id`,`user_id`) CLUSTERED
);
```

In addition, if the current time is also filled in by default when the data is being updated, the following statements can be used (but only the current-time related expressions can be filled in after `ON UPDATE`):

```sql
CREATE TABLE `bookshop`.`ratings` (
  `book_id` bigint,
  `user_id` bigint,
  `score` tinyint,
  `rated_at` datetime DEFAULT NOW() ON UPDATE NOW(),
  PRIMARY KEY (`book_id`,`user_id`) CLUSTERED
);
```

For more information on default values of different data types, see [default values](https://docs.pingcap.com/tidb/stable/data-type-default-values).
### Prevent duplicate values

If you need to prevent duplicate values in a column, you can use the `UNIQUE` constraint.

For example, to make sure that users' nicknames are unique, you can rewrite the table creation SQL statement for the `users` table like this:

```sql
CREATE TABLE `bookshop`.`users` (
  `id` bigint AUTO_RANDOM,
  `balance` decimal(15,2),
  `nickname` varchar(100) UNIQUE,
  PRIMARY KEY (`id`)
);
```

If you try to insert the same `nickname` in the `users` table, an error is returned.
### Prevent null values

If you need to prevent null values in a column, you can use the `NOT NULL` constraint.

Take user nicknames as an example. To ensure that a nickname is not only unique but is also not null, you can rewrite the SQL statement for creating the `users` table as follows:

```sql
CREATE TABLE `bookshop`.`users` (
  `id` bigint AUTO_RANDOM,
  `balance` decimal(15,2),
  `nickname` varchar(100) UNIQUE NOT NULL,
  PRIMARY KEY (`id`)
);
```
