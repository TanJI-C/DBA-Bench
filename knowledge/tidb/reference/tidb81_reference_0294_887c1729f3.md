# Control flow SQL functions: CASE, IF, IFNULL, and NULLIF

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/control-flow-functions.md`
- Source Title: `Control Flow Functions`
- Source Heading Path: `Control Flow Functions | Control Flow Functions > CASE | Control Flow Functions > IF() | Control Flow Functions > IFNULL() | Control Flow Functions > NULLIF()`
- Source Line Ranges: `5-142`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `control-flow-functions`, `case`, `if`, `ifnull`, `nullif`, `sql-functions`, `conditional-expressions`, `null-handling`, `examples`, `syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0294_887c1729f3`
- Source ID: `tidb-docs-8.1:functions-and-operators/control-flow-functions.md#control-flow-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `31f43ad8f6729b894d65ac990b6e51c259d437ddf182c2657563780e2316e6c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/control-flow-functions#control-flow-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/control-flow-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL reference syntax and examples for control flow functions such as CASE, IF(), IFNULL(), and NULLIF().
- Retrieval Keywords: Control Flow Functions, CASE, IF(), IFNULL(), NULLIF(), CASE WHEN condition THEN result ELSE default_result END, IF(condition, value_if_true, value_if_false), IFNULL(expr1,expr2), NULLIF(expr1,expr2), conditional logic, null handling, MySQL 8.0 flow-control functions
- Follow-up Guidance: The source includes example queries using WITH RECURSIVE and data CTEs to show odd/even results, NULL replacement, and NULLIF returning NULL when both arguments are the same.
- Classification Note: This is a SQL reference chunk because it defines supported control flow functions, gives their syntax, and shows example query results in TiDB.

## Official Source Content

# Control Flow Functions

TiDB supports all of the [control flow functions](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html) available in MySQL 8.0.

| Name                                                                                            | Description                       |
|:--------------------------------------------------------------------------------------------------|:----------------------------------|
| [`CASE`](#case)       | Case operator                     |
| [`IF()`](#if)         | If/else construct                 |
| [`IFNULL()`](#ifnull) | Null if/else construct            |
| [`NULLIF()`](#nullif) | Return `NULL` if expr1 = expr2      |
## CASE

The [`CASE`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#operator_case) operator enables you to perform conditional logic and customize query results based on specified conditions.

Syntax:

```sql
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    ...
    ELSE default_result
END
```

Example:

```sql
WITH RECURSIVE d AS (SELECT 1 AS n UNION ALL SELECT n+1 FROM d WHERE n<10)
SELECT n, CASE WHEN n MOD 2 THEN "odd" ELSE "even" END FROM d;
```

```
+----+----------------------------------------------+
| n  | CASE WHEN n MOD 2 THEN "odd" ELSE "even" END |
+----+----------------------------------------------+
|  1 | odd                                          |
|  2 | even                                         |
|  3 | odd                                          |
|  4 | even                                         |
|  5 | odd                                          |
|  6 | even                                         |
|  7 | odd                                          |
|  8 | even                                         |
|  9 | odd                                          |
| 10 | even                                         |
+----+----------------------------------------------+
10 rows in set (0.00 sec)
```
## IF()

The [`IF()`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#function_if) function enables you to perform different actions based on whether a value or expression is true or not.

Syntax:

```sql
IF(condition, value_if_true, value_if_false)
```

Example:

```sql
WITH RECURSIVE d AS (SELECT 1 AS n UNION ALL SELECT n+1 FROM d WHERE n<10)
SELECT n, IF(n MOD 2, "odd", "even") FROM d;
```

```
+----+----------------------------+
| n  | IF(n MOD 2, "odd", "even") |
+----+----------------------------+
|  1 | odd                        |
|  2 | even                       |
|  3 | odd                        |
|  4 | even                       |
|  5 | odd                        |
|  6 | even                       |
|  7 | odd                        |
|  8 | even                       |
|  9 | odd                        |
| 10 | even                       |
+----+----------------------------+
10 rows in set (0.00 sec)
```
## IFNULL()

The [`IFNULL(expr1,expr2)`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#function_ifnull) function is used to handle NULL values in queries. If `expr1` is not `NULL`, it returns `expr1`; otherwise, it returns `expr2`.

Example:

```sql
WITH data AS (SELECT NULL AS x UNION ALL SELECT 1 )
SELECT x, IFNULL(x,'x has no value') FROM data;
```

```
+------+----------------------------+
| x    | IFNULL(x,'x has no value') |
+------+----------------------------+
| NULL | x has no value             |
|    1 | 1                          |
+------+----------------------------+
2 rows in set (0.0006 sec)
```
## NULLIF()

The [`NULLIF(expr1,expr2)`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#function_nullif) function returns `NULL` if both arguments are the same or if the first argument is `NULL`. Otherwise, it returns the first argument.

Example:

```sql
WITH RECURSIVE d AS (SELECT 1 AS n UNION ALL SELECT n+1 FROM d WHERE n<10)
SELECT n, NULLIF(n+n, n+2) FROM d;
```

```
+----+------------------+
| n  | NULLIF(n+n, n+2) |
+----+------------------+
|  1 |                2 |
|  2 |             NULL |
|  3 |                6 |
|  4 |                8 |
|  5 |               10 |
|  6 |               12 |
|  7 |               14 |
|  8 |               16 |
|  9 |               18 |
| 10 |               20 |
+----+------------------+
10 rows in set (0.00 sec)
```

In this example, when `n` equals `2`, both `n+n` and `n+2` equal `4`, making both arguments the same and causing the function to return `NULL`.
