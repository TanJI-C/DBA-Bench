# Oracle to TiDB SQL syntax differences

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/oracle-functions-to-tidb.md`
- Source Title: `Comparisons between Functions and Syntax of Oracle and TiDB`
- Source Heading Path: `Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > String syntax | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Difference between `NULL` and an empty string | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Read and write to the same table in an `INSERT` statement | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Get the first n rows from a query | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Update multiple tables in an `UPDATE` statement | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Derived table alias | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Set operations | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Comment syntax | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Pagination | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of syntax > Sorting order on `NULL` values`
- Source Line Ranges: `47-170`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `oracle-compatibility`, `sql-syntax`, `string-literals`, `null-semantics`, `insert-select`, `limit`, `multi-table-update`, `derived-tables`, `set-operations`, `comments`, `pagination`, `order-by`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0462_fd070b9efb`
- Source ID: `tidb-docs-8.1:oracle-functions-to-tidb.md#comparisons-of-syntax`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6cd7b44e7a7cfc0f0bd32350d09a8e4a87e9bb47638ecb11d023af1b8b1f406`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/oracle-functions-to-tidb#comparisons-of-syntax
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/oracle-functions-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when checking Oracle-to-TiDB SQL syntax differences for string literals, `NULL` versus empty string behavior, `INSERT` restrictions, row limiting, multi-table `UPDATE`, derived table aliases, set operations, comments, pagination, and `ORDER BY` handling of `NULL` values.
- Retrieval Keywords: Oracle to TiDB SQL syntax differences, String syntax, Difference between NULL and an empty string, Read and write to the same table in an INSERT statement, Get the first n rows from a query, ROWNUM <= n, LIMIT n, Update multiple tables in an UPDATE statement, Derived table alias, MINUS, EXCEPT, Comment syntax, -- Comment, Pagination, LIMIT n OFFSET m, OFFSET m ROWS FETCH NEXT n ROWS ONLY, Sorting order on NULL values, ORDER BY column ASC, ORDER BY column DESC, NULLS FIRST, NULLS LAST, ISNULL(name), HQL running SQL statements with LIMIT results in an error
- Follow-up Guidance: The source provides equivalent TiDB statements for Oracle `MINUS`, pagination syntax, and `ORDER BY ... NULLS FIRST|LAST` cases.
- Classification Note: This chunk is reference content because it enumerates Oracle and TiDB SQL syntax differences with side-by-side examples and equivalent statements.

## Official Source Content

## Comparisons of syntax

This section describes some syntax differences between Oracle and TiDB.
### String syntax

In Oracle, a string can only be enclosed in single quotes (''). For example `'a'`.

In TiDB, a string can be enclosed in single quotes ('') or double quotes (""). For example, `'a'` and `"a"`.
### Difference between `NULL` and an empty string

Oracle does not distinguish between `NULL` and an empty string `''`, that is, `NULL` is equivalent to `''`.

TiDB distinguishes between `NULL` and an empty string `''`.
### Read and write to the same table in an `INSERT` statement

Oracle supports reading and writing to the same table in an `INSERT` statement. For example:

```sql
INSERT INTO table1 VALUES (field1,(SELECT field2 FROM table1 WHERE...))
```

TiDB does not support reading and writing to the same table in a `INSERT` statement. For example:

```sql
INSERT INTO table1 VALUES (field1,(SELECT T.fields2 FROM table1 T WHERE...))
```
### Get the first n rows from a query

In Oracle, to get the first n rows from a query, you can use the `ROWNUM <= n` clause. For example `ROWNUM <= 10`.

In TiDB, to get the first n rows from a query, you can use the `LIMIT n` clause. For example `LIMIT 10`. The Hibernate Query Language (HQL) running SQL statements with `LIMIT` results in an error. You need to change the Hibernate statements to SQL statements.
### Update multiple tables in an `UPDATE` statement

In Oracle, it is not necessary to list the specific field update relationship when updating multiple tables. For example:

```sql
UPDATE test1 SET(test1.name,test1.age) = (SELECT test2.name,test2.age FROM test2 WHERE test2.id=test1.id)
```

In TiDB, when updating multiple tables, you need to list all the specific field update relationships in `SET`. For example:

```sql
UPDATE test1,test2 SET test1.name=test2.name,test1.age=test2.age WHERE test1.id=test2.id
```
### Derived table alias

In Oracle, when querying multiple tables, it is unnecessary to add an alias to the derived table. For example:

```sql
SELECT * FROM (SELECT * FROM test)
```

In TiDB, when querying multiple tables, every derived table must have its own alias. For example:

```sql
SELECT * FROM (SELECT * FROM test) t
```
### Set operations

In Oracle, to get the rows that are in the first query result but not in the second, you can use the `MINUS` set operation. For example:

```sql
SELECT * FROM t1 MINUS SELECT * FROM t2
```

TiDB does not support the `MINUS` operation. You can use the `EXCEPT` set operation. For example:

```sql
SELECT * FROM t1 EXCEPT SELECT * FROM t2
```
### Comment syntax

In Oracle, the comment syntax is `--Comment`.

In TiDB, the comment syntax is `-- Comment`. Note that there is a white space after `--` in TiDB.
### Pagination

In Oracle, you can use the `OFFSET m ROWS` to skip `m` rows and use the `FETCH NEXT n ROWS ONLY`to fetch `n` rows. For example:

```sql
SELECT * FROM tables OFFSET 0 ROWS FETCH NEXT 2000 ROWS ONLY
```

In TiDB, you can use the `LIMIT n OFFSET m` to replace `OFFSET m ROWS FETCH NEXT n ROWS ONLY`. For example:

```sql
SELECT * FROM tables LIMIT 2000 OFFSET 0
```
### Sorting order on `NULL` values

In Oracle, `NULL` values are sorted by the `ORDER BY` clause in the following cases:

- In the `ORDER BY column ASC` statement, `NULL` values are returned last.

- In the `ORDER BY column DESC` statement, `NULL` values are returned first.

- In the `ORDER BY column [ASC|DESC] NULLS FIRST` statement, `NULL` values are returned before non-NULL values. Non-NULL values are returned in ascending order or descending order specified in `ASC|DESC`.

- In the `ORDER BY column [ASC|DESC] NULLS LAST` statement, `NULL` values are returned after non-NULL values. Non-NULL values are returned in ascending order or descending order specified in `ASC|DESC`.

In TiDB, `NULL` values are sorted by the `ORDER BY` clause in the following cases:

- In the `ORDER BY column ASC` statement, `NULL` values are returned first.

- In the `ORDER BY column DESC` statement, `NULL` values are returned last.

The following table shows some examples of equivalent `ORDER BY` statements in Oracle and TiDB:

| `ORDER BY` in Oracle | Equivalent statements in TiDB |
| :------------------- | :----------------- |
| `SELECT * FROM t1 ORDER BY name NULLS FIRST;`      | `SELECT * FROM t1 ORDER BY name;`  |
| `SELECT * FROM t1 ORDER BY name DESC NULLS LAST;`  | `SELECT * FROM t1 ORDER BY name DESC;` |
| `SELECT * FROM t1 ORDER BY name DESC NULLS FIRST;` | `SELECT * FROM t1 ORDER BY ISNULL(name) DESC, name DESC;` |
| `SELECT * FROM t1 ORDER BY name ASC NULLS LAST;`   | `SELECT * FROM t1 ORDER BY ISNULL(name), name;` |
