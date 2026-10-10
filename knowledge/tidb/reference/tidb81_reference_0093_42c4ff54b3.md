# Create table basics, columns, and primary key selection

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-table.md`
- Source Title: `Create a Table`
- Source Heading Path: `Create a Table | Create a Table > Before you start | Create a Table > What is a table | Create a Table > Name a table | Create a Table > Define columns | Create a Table > Select primary key`
- Source Line Ranges: `5-133`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `create-table`, `schema-design`, `table-definition`, `column-definition`, `data-types`, `primary-key`, `clustered-index`, `auto-random`, `auto-increment`, `hotspot`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0093_42c4ff54b3`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-table.md#create-a-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `20e7ceade94d48fb48dcad3b4fedecdf8974d60b3ea58e4904922b47ee7e0bc2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#create-a-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving guidance on defining a TiDB table with CREATE TABLE, choosing column data types, and selecting a primary key with clustered-index and hotspot considerations.
- Retrieval Keywords: CREATE TABLE, bookshop.users, bookshop.books, column definitions, bigint, varchar(100), decimal(15,2), enum('Magazine', 'Novel', 'Life', 'Arts', 'Comics', 'Education & Reference', 'Humanities & Social Sciences', 'Science & Technology', 'Kids', 'Sports'), datetime, PRIMARY KEY, CLUSTERED, NONCLUSTERED, @@global.tidb_enable_clustered_index, _tidb_rowid, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, AUTO_INCREMENT, AUTO_RANDOM, write hotspots, clustered indexes
- Follow-up Guidance: The source also points to clustered indexes, shard-row-id-bits, PRE_SPLIT_REGIONS, AUTO_RANDOM, and Troubleshoot Hotspot Issues for more information about primary key behavior and hotspot handling.
- Classification Note: This chunk is reference content because it explains the CREATE TABLE statement structure, column definition syntax, supported example data types, and primary key characteristics in TiDB.

## Official Source Content

# Create a Table

This document introduces how to create tables using the SQL statement and the related best practices. An example of the TiDB-based [Bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) application is provided to illustrate the best practices.
## Before you start

Before reading this document, make sure that the following tasks are completed:

- [Build a {{{ .starter }}} Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
- Read [Schema Design Overview](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview).
- [Create a Database](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-database).
## What is a table

A [table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview#table) is a logical object in TiDB cluster that is subordinate to the [database](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview#database). It is used to store the data sent from SQL statements. Tables save data records in the form of rows and columns. A table has at least one column. If you have defined `n` columns, each row of data has exactly the same fields as the `n` columns.
## Name a table

The first step for creating a table is to give your table a name. Do not use meaningless names that will cause great distress to yourself or your colleagues in the future. It is recommended that you follow your company or organization's table naming convention.

The `CREATE TABLE` statement usually takes the following form:

```sql
CREATE TABLE {table_name} ( {elements} );
```

**Parameter description**

- `{table_name}`: The name of the table to be created.
- `{elements}`: A comma-separated list of table elements, such as column definitions and primary key definitions.

Suppose you need to create a table to store the user information in the `bookshop` database.

Note that you cannot execute the following SQL statement yet because not a single column has been added.

```sql
CREATE TABLE `bookshop`.`users` (
);
```
## Define columns

A **column** is subordinate to a table. Each table has at least one column. Columns provide a structure to a table by dividing the values in each row into small cells of a single data type.

Column definitions typically take the following form.

```
{column_name} {data_type} {column_qualification}
```

**Parameter description**

- `{column_name}`: The column name.
- `{data_type}`: The column [data type](https://docs.pingcap.com/tidb/stable/data-type-overview).
- `{column_qualification}`: Column qualifications, such as **column-level constraints** or [generated column](https://docs.pingcap.com/tidb/stable/generated-columns) clauses.

You can add some columns to the `users` table, such as the unique identifier `id`, `balance` and `nickname`.

```sql
CREATE TABLE `bookshop`.`users` (
  `id` bigint,
  `nickname` varchar(100),
  `balance` decimal(15,2)
);
```

In the above statement, a field is defined with the name `id` and the type [bigint](https://docs.pingcap.com/tidb/stable/data-type-numeric#bigint-type). This is used to represent a unique user identifier. This means that all user identifiers should be of the `bigint` type.

Then, a field named `nickname` is defined, which is the [varchar](https://docs.pingcap.com/tidb/stable/data-type-string#varchar-type) type, with a length limit of 100 characters. This means that the `nicknames` of the users use the `varchar` type and are not longer than 100 characters.

Finally, a field named `balance` is added, which is the [decimal](https://docs.pingcap.com/tidb/stable/data-type-numeric#decimal-type) type, with a **precision** of `15` and a **scale** of `2`. **Precision** represents the total number of digits in the field, and **scale** represents the number of decimal places. For example, `decimal(5,2)` means a precision of `5` and a scale of `2`, with the range from `-999.99` to `999.99`. `decimal(6,1)` means a precision of `6` and a scale of `1`, with the range from `-99999.9` to `99999.9`. **decimal** is a [fixed-point types](https://docs.pingcap.com/tidb/stable/data-type-numeric#fixed-point-types), which can be used to store numbers accurately. In scenarios where accurate numbers are needed (for example, user property-related), make sure that you use the **decimal** type.

TiDB supports many other column data types, including the [integer types](https://docs.pingcap.com/tidb/stable/data-type-numeric#integer-types), [floating-point types](https://docs.pingcap.com/tidb/stable/data-type-numeric#floating-point-types), [fixed-point types](https://docs.pingcap.com/tidb/stable/data-type-numeric#fixed-point-types), [date and time types](https://docs.pingcap.com/tidb/stable/data-type-date-and-time), and the [enum type](https://docs.pingcap.com/tidb/stable/data-type-string#enum-type). You can refer to the supported column [data types](https://docs.pingcap.com/tidb/stable/data-type-overview) and use the **data types** that match the data you want to save in the database.

To make it a bit more complex, you can define a `books` table which will be the core of the `bookshop` data. The `books` table contains fields for the book's ids, titles, types (for example, magazine, novel, life, arts), stock, prices, and publication dates.

```sql
CREATE TABLE `bookshop`.`books` (
  `id` bigint NOT NULL,
  `title` varchar(100),
  `type` enum('Magazine', 'Novel', 'Life', 'Arts', 'Comics', 'Education & Reference', 'Humanities & Social Sciences', 'Science & Technology', 'Kids', 'Sports'),
  `published_at` datetime,
  `stock` int,
  `price` decimal(15,2)
);
```

This table contains more data types than the `users` table.

- [int](https://docs.pingcap.com/tidb/stable/data-type-numeric#integer-types): It is recommended to use the type of right size to avoid using too much disk or even affecting performance (too large a type range) or data overflow (too small a data type range).
- [datetime](https://docs.pingcap.com/tidb/stable/data-type-date-and-time): The **datetime** type can be used to store time values.
- [enum](https://docs.pingcap.com/tidb/stable/data-type-string#enum-type): The enum type can be used to store a limited selection of values.
## Select primary key

A [primary key](https://docs.pingcap.com/tidb/stable/constraints#primary-key) is a column or a set of columns in a table whose values uniquely identify a row in the table.

> **Note:**
>
> The default definition of **primary key** in TiDB is different from that in [InnoDB](https://dev.mysql.com/doc/refman/8.0/en/innodb-storage-engine.html)(the common storage engine of MySQL).
>
> - In **InnoDB**: A **primary key** is unique, not null, and **index clustered**.
>
> - In TiDB: A **primary key** is unique and is not null. But the primary key is not guaranteed to be a **clustered index**. Instead, another set of keywords `CLUSTERED` / `NONCLUSTERED` additionally controls whether the **primary key** is a **clustered index**. If the keyword is not specified, it is controlled by the system variable `@@global.tidb_enable_clustered_index`, as described in [clustered indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes).

The **primary key** is defined in the `CREATE TABLE` statement. The [primary key constraint](https://docs.pingcap.com/tidb/stable/constraints#primary-key) requires that all constrained columns contain only non-NULL values.

A table can be created without a **primary key** or with a non-integer **primary key**. In this case, TiDB creates a `_tidb_rowid` as an **implicit primary key**. The implicit primary key `_tidb_rowid`, because of its monotonically increasing nature, might cause write hotspots in write-intensive scenarios. Therefore, if your application is write-intensive, consider sharding data using the [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits) and [`PRE_SPLIT_REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#pre_split_regions) parameters. However, this might lead to read amplification, so you need to make your own trade-off.

When the **primary key** of a table is an [integer type](https://docs.pingcap.com/tidb/stable/data-type-numeric#integer-types) and `AUTO_INCREMENT` is used, hotspots cannot be avoided by using `SHARD_ROW_ID_BITS`. If you need to avoid hotspots and do not need a continuous and incremental primary key, you can use [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) instead of `AUTO_INCREMENT` to eliminate row ID continuity.

For more information on how to handle hotspot issues, refer to [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues).

Following the [guidelines for selecting primary key](#guidelines-to-follow-when-selecting-primary-key), the following example shows how an `AUTO_RANDOM` primary key is defined in the `users` table.

```sql
CREATE TABLE `bookshop`.`users` (
  `id` bigint AUTO_RANDOM,
  `balance` decimal(15,2),
  `nickname` varchar(100),
  PRIMARY KEY (`id`)
);
```
