# Window functions overview and function examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/window-functions.md`
- Source Title: `Window Functions`
- Source Heading Path: `Window Functions | Window Functions > [`CUME_DIST()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_cume-dist) | Window Functions > [`DENSE_RANK()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_dense-rank) | Window Functions > [`FIRST_VALUE()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_first-value) | Window Functions > [`LAG()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_lag) | Window Functions > [`LAST_VALUE()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_last-value) | Window Functions > [`LEAD()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_lead)`
- Source Line Ranges: `5-270`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `window-functions`, `system-variables`, `parser-keywords`, `pipelined-execution`, `high-precision`, `pushdown`, `cume-dist`, `dense-rank`, `first-value`, `lag`, `last-value`, `lead`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0359_64b80c28db`
- Source ID: `tidb-docs-8.1:functions-and-operators/window-functions.md#window-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `563bd266341b365cc87073a0ac1c01c10b605e11f05e4c6e01a3b49095bc7740`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions#window-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/window-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL window function support, examples of CUME_DIST(), DENSE_RANK(), FIRST_VALUE(), LAG(), LAST_VALUE(), or LEAD(), or related system variables and TiFlash pushdown notes.
- Retrieval Keywords: window functions, MySQL 8.0 window functions, tidb_enable_window_function, tidb_enable_pipelined_window_function, windowing_use_high_precision, keywords in the parser, errors parsing SQL statements after upgrading TiDB, pipeline execution algorithm for window functions, high precision mode for window functions, TiFlash supported pushdown calculations, GROUP_CONCAT(), APPROX_PERCENTILE(), GROUP BY aggregate functions as window functions, CUME_DIST(), ORDER BY clause with CUME_DIST(), DENSE_RANK(), RANK(), FIRST_VALUE(), PARTITION BY, LAG(expr [, num [, default]]), LAST_VALUE(), LEAD(expr [, num [,default]]), ROW_NUMBER(), PERCENT_RANK(), NTILE(), NTH_VALUE()
- Follow-up Guidance: The source also points to MySQL Window Functions, TiDB system variables, TiDB keywords, aggregate GROUP BY functions, and the TiFlash supported pushdown calculations list.
- Classification Note: This is reference content because it defines window function behavior, lists supported functions, names exact system variables, and shows SQL examples with result sets.

## Official Source Content

# Window Functions

The usage of window functions in TiDB is similar to that in MySQL 8.0. For details, see [MySQL Window Functions](https://dev.mysql.com/doc/refman/8.0/en/window-functions.html).

In TiDB, you can control window functions using the following system variables:

- [`tidb_enable_window_function`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_window_function): because window functions reserve additional [keywords](https://docs.pingcap.com/tidb/stable/keywords) in the parser, TiDB provides this variable to disable window functions. If you receive errors parsing SQL statements after upgrading TiDB, try setting this variable to `OFF`.
- [`tidb_enable_pipelined_window_function`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_pipelined_window_function): you can use this variable to disable pipeline execution algorithm for window functions.
- [`windowing_use_high_precision`](https://docs.pingcap.com/tidb/stable/system-variables#windowing_use_high_precision): you can use this variable to disable high precision mode for window functions.

The window functions [listed here](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations) can be pushed down to TiFlash.

Except for `GROUP_CONCAT()` and `APPROX_PERCENTILE()`, TiDB supports using all [`GROUP BY` aggregate functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions) as window functions. In addition, TiDB supports the following window functions:

| Function name                     | Feature description |
| :-------------------------------- | :------------------------------------- |
| [`CUME_DIST()`](#cume_dist)       | Returns the cumulative distribution of a value within a group of values. |
| [`DENSE_RANK()`](#dense_rank)     | Returns the rank of the current row within the partition, and the rank is without gaps. |
| [`FIRST_VALUE()`](#first_value)   | Returns the expression value of the first row in the current window. |
| [`LAG()`](#lag)                   | Returns the expression value from the row that precedes the current row by N rows within the partition. |
| [`LAST_VALUE()`](#last_value)     | Returns the expression value of the last row in the current window. |
| [`LEAD()`](#lead)                 | Returns the expression value from the row that follows the current row by N rows within the partition. |
| [`NTH_VALUE()`](#nth_value)       | Returns the expression value from the N-th row of the current window. |
| [`NTILE()`](#ntile)               | Divides a partition into N buckets, assigns the bucket number to each row in the partition, and returns the bucket number of the current row within the partition. |
| [`PERCENT_RANK()`](#percent_rank) | Returns the percentage of partition values that are less than the value in the current row. |
| [`RANK()`](#rank)                 | Returns the rank of the current row within the partition. The rank might have gaps. |
| [`ROW_NUMBER()`](#row_number)     | Returns the number of the current row in the partition. |
## [`CUME_DIST()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_cume-dist)

`CUME_DIST()` calculates the cumulative distribution of a value within a group of values. Note that you need to use the `ORDER BY` clause with `CUME_DIST()` to sort the group of values. Otherwise, this function will not return the expected values.

```sql
WITH RECURSIVE cte(n) AS (
    SELECT 1
    UNION
    SELECT
        n+2
    FROM
        cte
    WHERE
        n<6
)
SELECT
    *,
    CUME_DIST() OVER(ORDER BY n)
FROM
    cte;
```

```
+------+------------------------------+
| n    | CUME_DIST() OVER(ORDER BY n) |
+------+------------------------------+
|    1 |                         0.25 |
|    3 |                          0.5 |
|    5 |                         0.75 |
|    7 |                            1 |
+------+------------------------------+
4 rows in set (0.00 sec)
```
## [`DENSE_RANK()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_dense-rank)

The `DENSE_RANK()` function returns the rank of the current row. It is similar to [`RANK()`](#rank) but does not leave any gaps in case of ties (rows that share the same values and order conditions).

```sql
SELECT
    *,
    DENSE_RANK() OVER (ORDER BY n)
FROM (
    SELECT 5 AS 'n'
    UNION ALL
    SELECT 8
    UNION ALL
    SELECT 5
    UNION ALL
    SELECT 30
    UNION ALL
    SELECT 31
    UNION ALL
    SELECT 32) a;
```

```
+----+--------------------------------+
| n  | DENSE_RANK() OVER (ORDER BY n) |
+----+--------------------------------+
|  5 |                              1 |
|  5 |                              1 |
|  8 |                              2 |
| 30 |                              3 |
| 31 |                              4 |
| 32 |                              5 |
+----+--------------------------------+
6 rows in set (0.00 sec)
```
## [`FIRST_VALUE()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_first-value)

The `FIRST_VALUE(expr)` returns the first value in a window.

The following example uses two different window definitions:

- `PARTITION BY n MOD 2 ORDER BY n` partitions the data in table `a` into two groups: `1, 3` and `2, 4`. So it returns either `1` or `2` as those are the first values of those groups.
- `PARTITION BY n <= 2 ORDER BY n` partitions the data in table `a` into two groups: `1, 2` and `3, 4` So it returns either `1` or `3` depending on which group `n` belongs to.

```sql
SELECT
    n,
    FIRST_VALUE(n) OVER (PARTITION BY n MOD 2 ORDER BY n),
    FIRST_VALUE(n) OVER (PARTITION BY n <= 2 ORDER BY n)
FROM (
    SELECT 1 AS 'n'
    UNION
    SELECT 2
    UNION
    SELECT 3
    UNION
    SELECT 4
) a
ORDER BY
    n;
```

```
+------+-------------------------------------------------------+------------------------------------------------------+
| n    | FIRST_VALUE(n) OVER (PARTITION BY n MOD 2 ORDER BY n) | FIRST_VALUE(n) OVER (PARTITION BY n <= 2 ORDER BY n) |
+------+-------------------------------------------------------+------------------------------------------------------+
|    1 |                                                     1 |                                                    1 |
|    2 |                                                     2 |                                                    1 |
|    3 |                                                     1 |                                                    3 |
|    4 |                                                     2 |                                                    3 |
+------+-------------------------------------------------------+------------------------------------------------------+
4 rows in set (0.00 sec)
```
## [`LAG()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_lag)

The `LAG(expr [, num [, default]])` function returns the value of `expr` from the row that is `num` rows preceding the current row. If such row does not exist, `default` is returned. By default, `num` is `1` and `default` is `NULL` when they are not specified.

In the following example, because `num` is not specified, `LAG(n)` returns the value of `n` in the previous row. When `n` is 1, because the previous row does not exist and `default` is not specified, `LAG(1)` returns `NULL`.

```sql
WITH RECURSIVE cte(n) AS (
    SELECT 1
    UNION
    SELECT
        n+1
    FROM
        cte
    WHERE
        n<10
)
SELECT
    n,
    LAG(n) OVER ()
FROM
    cte;
```

```
+------+----------------+
| n    | LAG(n) OVER () |
+------+----------------+
|    1 |           NULL |
|    2 |              1 |
|    3 |              2 |
|    4 |              3 |
|    5 |              4 |
|    6 |              5 |
|    7 |              6 |
|    8 |              7 |
|    9 |              8 |
|   10 |              9 |
+------+----------------+
10 rows in set (0.01 sec)
```
## [`LAST_VALUE()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_last-value)

The `LAST_VALUE()` function returns the last value in the window.

```sql
WITH RECURSIVE cte(n) AS (
    SELECT
        1
    UNION
    SELECT
        n+1
    FROM
        cte
    WHERE
        n<10
)
SELECT
    n,
    LAST_VALUE(n) OVER (PARTITION BY n<=5)
FROM
    cte
ORDER BY
    n;
```

```
+------+----------------------------------------+
| n    | LAST_VALUE(n) OVER (PARTITION BY n<=5) |
+------+----------------------------------------+
|    1 |                                      5 |
|    2 |                                      5 |
|    3 |                                      5 |
|    4 |                                      5 |
|    5 |                                      5 |
|    6 |                                     10 |
|    7 |                                     10 |
|    8 |                                     10 |
|    9 |                                     10 |
|   10 |                                     10 |
+------+----------------------------------------+
10 rows in set (0.00 sec)
```
## [`LEAD()`](https://dev.mysql.com/doc/refman/8.0/en/window-function-descriptions.html#function_lead)

The `LEAD(expr [, num [,default]])` function returns the value of `expr` from the row that is `num` rows following the current row. If such row does not exist, `default` is returned. By default, `num` is `1` and `default` is `NULL` when they are not specified.

In the following example, because `num` is not specified, `LEAD(n)` returns the value of `n` in the next row following the current row. When `n` is 10, because the next row does not exist and `default` is not specified, `LEAD(10)` returns `NULL`.

```sql
WITH RECURSIVE cte(n) AS (
    SELECT
        1
    UNION
    SELECT
        n+1
    FROM
        cte
    WHERE
        n<10
)
SELECT
    n,
    LEAD(n) OVER ()
FROM
    cte;
```

```
+------+-----------------+
| n    | LEAD(n) OVER () |
+------+-----------------+
|    1 |               2 |
|    2 |               3 |
|    3 |               4 |
|    4 |               5 |
|    5 |               6 |
|    6 |               7 |
|    7 |               8 |
|    8 |               9 |
|    9 |              10 |
|   10 |            NULL |
+------+-----------------+
10 rows in set (0.00 sec)
```
