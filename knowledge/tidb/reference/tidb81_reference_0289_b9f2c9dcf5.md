# Supported aggregate functions and GROUP BY modifiers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/aggregate-group-by-functions.md`
- Source Title: `Aggregate (GROUP BY) Functions`
- Source Heading Path: `Aggregate (GROUP BY) Functions | Aggregate (GROUP BY) Functions > Supported aggregate functions | Aggregate (GROUP BY) Functions > GROUP BY modifiers`
- Source Line Ranges: `5-93`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `aggregate-functions`, `group-by`, `count`, `sum`, `avg`, `group-concat`, `approx-percentile`, `approx-count-distinct`, `with-rollup`, `window-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0289_b9f2c9dcf5`
- Source ID: `tidb-docs-8.1:functions-and-operators/aggregate-group-by-functions.md#aggregate-group-by-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `72f4cd070ed8fc78ced245db3f4a5d8e9d63a8a77126700a954854f5ac52a1f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions#aggregate-group-by-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/aggregate-group-by-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up which TiDB aggregate functions are supported, whether they can be used as Window functions, or whether `GROUP BY` supports `WITH ROLLUP`.
- Retrieval Keywords: Aggregate (GROUP BY) Functions, supported aggregate functions, COUNT(), COUNT(DISTINCT), SUM(), AVG(), MAX(), MIN(), GROUP_CONCAT(), VARIANCE(), VAR_POP(), STD(), STDDEV(), STDDEV_POP, VAR_SAMP(), STDDEV_SAMP(), JSON_ARRAYAGG(), JSON_OBJECTAGG(), APPROX_PERCENTILE(expr, constant_integer_expr), APPROX_COUNT_DISTINCT(expr, [expr...]), NULL values, no GROUP BY clause, Window functions, WITH ROLLUP, GROUP BY modifiers
- Follow-up Guidance: For `WITH ROLLUP`, the content points to the `GROUP BY modifiers` document for more information.
- Classification Note: This is reference content because it enumerates supported aggregate functions, documents exact function names and behavior notes, and states the `GROUP BY` modifier support.

## Official Source Content

# Aggregate (GROUP BY) Functions

This document describes details about the supported aggregate functions in TiDB.
## Supported aggregate functions

This section describes the supported MySQL `GROUP BY` aggregate functions in TiDB.

| Name                                                                                                           | Description                                       |
|:---------------------------------------------------------------------------------------------------------------|:--------------------------------------------------|
| [`COUNT()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_count)                   | Return a count of the number of rows returned     |
| [`COUNT(DISTINCT)`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_count-distinct)  | Return the count of a number of different values  |
| [`SUM()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_sum)                       | Return the sum                                    |
| [`AVG()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_avg)                       | Return the average value of the argument          |
| [`MAX()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_max)                       | Return the maximum value                          |
| [`MIN()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_min)                       | Return the minimum value                          |
| [`GROUP_CONCAT()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_group-concat)     | Return a concatenated string                      |
| [`VARIANCE()`, `VAR_POP()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_var-pop) | Return the population standard variance           |
| [`STD()`, `STDDEV()`, `STDDEV_POP`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_std) | Return the population standard deviation      |
| [`VAR_SAMP()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_var-samp)             | Return the sample variance                        |
| [`STDDEV_SAMP()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_stddev-samp)       | Return the sample standard deviation              |
| [`JSON_ARRAYAGG()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-aggregate#json_arrayagg)         | Return the result set as a single JSON array      |
| [`JSON_OBJECTAGG()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-aggregate#json_objectagg)       | Return the result set as a single JSON object containing key-value pairs |

- Unless otherwise stated, group functions ignore `NULL` values.
- If you use a group function in a statement containing no `GROUP BY` clause, it is equivalent to grouping on all rows.

In addition, TiDB also provides the following aggregate functions:

+ `APPROX_PERCENTILE(expr, constant_integer_expr)`

    This function returns the percentile of `expr`. The `constant_integer_expr` argument indicates the percentage value which is a constant integer in the range of `[1,100]`. A percentile P<sub>k</sub> (`k` represents percentage) indicates that there are at least `k%` values in the data set that are less than or equal to P<sub>k</sub>.

    This function only supports the [numeric type](https://docs.pingcap.com/tidb/stable/data-type-numeric) and the [date and time type](https://docs.pingcap.com/tidb/stable/data-type-date-and-time) as the returned type of `expr`. For other returned types, `APPROX_PERCENTILE` only returns `NULL`.

    The following example shows how to calculate the fiftieth percentile of a `INT` column:

    ```sql
    DROP TABLE IF EXISTS t;
    CREATE TABLE t(a INT);
    INSERT INTO t VALUES(1), (2), (3);
    ```

    ```sql
    SELECT APPROX_PERCENTILE(a, 50) FROM t;
    ```

    ```sql
    +--------------------------+
    | APPROX_PERCENTILE(a, 50) |
    +--------------------------+
    |                        2 |
    +--------------------------+
    1 row in set (0.00 sec)
    ```

+ `APPROX_COUNT_DISTINCT(expr, [expr...])`

    This function is similar to `COUNT(DISTINCT)` in counting the number of distinct values but returns an approximate result. It uses the `BJKST` algorithm, significantly reducing memory consumption when processing large datasets with a power-law distribution. Moreover, for low-cardinality data, this function provides high accuracy while maintaining efficient CPU utilization.

    The following example shows how to use this function:

    ```sql
    DROP TABLE IF EXISTS t;
    CREATE TABLE t(a INT, b INT, c INT);
    INSERT INTO t VALUES(1, 1, 1), (2, 1, 1), (2, 2, 1), (3, 1, 1), (5, 1, 2), (5, 1, 2), (6, 1, 2), (7, 1, 2);
    ```

    ```sql
    SELECT APPROX_COUNT_DISTINCT(a, b) FROM t GROUP BY c;
    ```

    ```
    +-----------------------------+
    | approx_count_distinct(a, b) |
    +-----------------------------+
    |                           3 |
    |                           4 |
    +-----------------------------+
    2 rows in set (0.00 sec)
    ```

Except for the `GROUP_CONCAT()`, `APPROX_PERCENTILE()`, and `APPROX_COUNT_DISTINCT` functions, all the preceding functions can serve as [Window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions).
## GROUP BY modifiers

Starting from v7.4.0, the `GROUP BY` clause of TiDB supports the `WITH ROLLUP` modifier. For more information, see [GROUP BY modifiers](https://docs.pingcap.com/tidb/stable/functions-and-operators/group-by-modifier).
