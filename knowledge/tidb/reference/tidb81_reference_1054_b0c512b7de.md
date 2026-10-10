# User-defined variables syntax, usage, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/user-defined-variables.md`
- Source Title: `User-Defined Variables`
- Source Heading Path: `User-Defined Variables | User-Defined Variables > Set the user-defined variables | User-Defined Variables > Read the user-defined variables | User-Defined Variables > MySQL compatibility`
- Source Line Ranges: `5-161`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `user-defined-variables`, `session-scope`, `set`, `select`, `prepare`, `expressions`, `binary-literals`, `cast`, `mysql-compatibility`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1054_b0c512b7de`
- Source ID: `tidb-docs-8.1:user-defined-variables.md#user-defined-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9546285da18847e643c8fd7f22ce5c26f368cc28f30d86cc912fb52bd0ac641a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/user-defined-variables#user-defined-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/user-defined-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about TiDB user-defined variables syntax, session scope, reading or setting `@var_name`, behavior of uninitialized variables, `PREPARE` usage, binary literal handling, or MySQL compatibility differences.
- Retrieval Keywords: User-Defined Variables, @var_name, session-specific, SET @var_name = expr, SET @var_name := expr, SELECT @a1, @a2, @a3, SELECT @a4 := @a1+@a2+@a3, PREPARE stmt FROM @s, EXECUTE stmt USING @a, @b, b'1000001', CAST(b'1000001' AS UNSIGNED), uninitialized variable NULL string, contents of user-defined variables are not recognized as identifiers, SELECT ... INTO <variable>, experimental feature, MySQL compatibility
- Follow-up Guidance: The source also states that user-defined variables are experimental and that, except for `SELECT ... INTO <variable>`, the syntax supported in MySQL and TiDB is identical.
- Classification Note: This is reference content because it defines the syntax, semantics, examples, and compatibility notes for TiDB SQL user-defined variables.

## Official Source Content

# User-Defined Variables

This document describes the concept of user-defined variables in TiDB and the methods to set and read the user-defined variables.

> **Warning:**
>
> User-defined variables are still an experimental feature. It is **NOT** recommended that you use them in the production environment.

The format of the user-defined variables is `@var_name`. The characters that compose `var_name` can be any characters that can compose an identifier, including the numbers `0-9`, the letters `a-zA-Z`, the underscore `_`, the dollar sign `$`, and the UTF-8 characters. In addition, it also includes the English period `.`. The user-defined variables are case-insensitive.

The user-defined variables are session-specific, which means a user variable defined by one client connection cannot be seen or used by other client connections.
## Set the user-defined variables

You can use the [`SET` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable) to set a user-defined variable, and the syntax is `SET @var_name = expr [, @var_name = expr] ...;`. For example:

```sql
SET @favorite_db = 'TiDB';
```

```sql
SET @a = 'a', @b = 'b', @c = 'c';
```

For the assignment operator, you can also use `:=`. For example:

```sql
SET @favorite_db := 'TiDB';
```

The content to the right of the assignment operator can be any valid expression. For example:

```sql
SET @c = @a + @b;
```

```sql
SET @c = b'1000001' + b'1000001';
```
## Read the user-defined variables

To read a user-defined variable, you can use the `SELECT` statement to query:

```sql
SELECT @a1, @a2, @a3
```

```
+------+------+------+
| @a1  | @a2  | @a3  |
+------+------+------+
|    1 |    2 |    4 |
+------+------+------+
```

You can also assign values in the `SELECT` statement:

```sql
SELECT @a1, @a2, @a3, @a4 := @a1+@a2+@a3;
```

```
+------+------+------+--------------------+
| @a1  | @a2  | @a3  | @a4 := @a1+@a2+@a3 |
+------+------+------+--------------------+
|    1 |    2 |    4 |                  7 |
+------+------+------+--------------------+
```

Before the variable `@a4` is modified or the connection is closed, its value is always `7`.

If a hexadecimal literal or binary literal is used when setting the user-defined variable, TiDB will treat it as a binary string. If you want to set it to a number, you can manually add the `CAST` conversion, or use the numeric operator in the expression:

```sql
SET @v1 = b'1000001';
SET @v2 = b'1000001'+0;
SET @v3 = CAST(b'1000001' AS UNSIGNED);
```

```sql
SELECT @v1, @v2, @v3;
```

```
+------+------+------+
| @v1  | @v2  | @v3  |
+------+------+------+
| A    | 65   | 65   |
+------+------+------+
```

If you refer to a user-defined variable that has not been initialized, it has a value of NULL and a type of string.

```sql
SELECT @not_exist;
```

```
+------------+
| @not_exist |
+------------+
| NULL       |
+------------+
```

In addition to using the `SELECT` statement to read the user-defined variables, another common usage is the `PREPARE` statement. For example:

```sql
SET @s = 'SELECT SQRT(POW(?,2) + POW(?,2)) AS hypotenuse';
PREPARE stmt FROM @s;
SET @a = 6;
SET @b = 8;
EXECUTE stmt USING @a, @b;
```

```
+------------+
| hypotenuse |
+------------+
|         10 |
+------------+
```

The contents of the user-defined variables are not recognized as identifiers in the SQL statements. For example:

```sql
SELECT * from t;
```

```
+---+
| a |
+---+
| 1 |
+---+
```

```sql
SET @col = "`a`";
SELECT @col FROM t;
```

```
+------+
| @col |
+------+
| `a`  |
+------+
```
## MySQL compatibility

Except for `SELECT ... INTO <variable>`, the syntax supported in MySQL and TiDB is identical.

For more information, see [User-Defined Variables in MySQL](https://dev.mysql.com/doc/refman/8.0/en/user-variables.html).
