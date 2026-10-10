# Vector function and operator overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-functions-and-operators.md`
- Source Title: `Vector Functions and Operators`
- Source Heading Path: `Vector Functions and Operators | Vector Functions and Operators > Vector functions | Vector Functions and Operators > Extended built-in functions and operators`
- Source Line Ranges: `5-98`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `vector`, `functions`, `operators`, `distance`, `arithmetic`, `aggregate`, `comparison`, `control-flow`, `cast`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0921_4a69e702c5`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-functions-and-operators.md#vector-functions-and-operators`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d5e1d69504395faf8545882360a03fe039cba60f9c4857a9b29f3bd54b567c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-functions-and-operators#vector-functions-and-operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-functions-and-operators.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which Vector Functions and Operators are available for Vector data types and which built-in SQL functions and operators are extended to support vector operations.
- Retrieval Keywords: Vector Functions and Operators, Vector data types, VEC_L2_DISTANCE, VEC_COSINE_DISTANCE, VEC_NEGATIVE_INNER_PRODUCT, VEC_L1_DISTANCE, VEC_DIMS, VEC_L2_NORM, VEC_FROM_TEXT, VEC_AS_TEXT, extended built-in functions and operators, vector element-wise addition operator, vector element-wise subtraction operator, COUNT(), COUNT(DISTINCT), MAX(), MIN(), BETWEEN ... AND ..., COALESCE(), <=>, GREATEST(), IN(), IS NULL, ISNULL(), LEAST(), NOT IN(), CASE, IF(), IFNULL(), NULLIF(), CAST(), CONVERT(), Vector Data Type | Arithmetic, Vector Data Type | Comparison, Vector Data Type | Cast
- Follow-up Guidance: The source points to Vector Data Type sections for more information about arithmetic, comparison, and CAST() behavior.
- Classification Note: This is reference content because it enumerates available vector-specific functions and the built-in SQL operators and functions extended for vector support.

## Official Source Content

# Vector Functions and Operators

This document lists the functions and operators available for Vector data types.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Vector functions

The following functions are designed specifically for [Vector data types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types).

**Vector distance functions:**

| Function Name                                               | Description                                                      |
| ----------------------------------------------------------- | ---------------------------------------------------------------- |
| [`VEC_L2_DISTANCE`](#vec_l2_distance)                       | Calculates L2 distance (Euclidean distance) between two vectors  |
| [`VEC_COSINE_DISTANCE`](#vec_cosine_distance)               | Calculates the cosine distance between two vectors               |
| [`VEC_NEGATIVE_INNER_PRODUCT`](#vec_negative_inner_product) | Calculates the negative of the inner product between two vectors |
| [`VEC_L1_DISTANCE`](#vec_l1_distance)                       | Calculates L1 distance (Manhattan distance) between two vectors  |

**Other vector functions:**

| Function Name                     | Description                                         |
| --------------------------------- | --------------------------------------------------- |
| [`VEC_DIMS`](#vec_dims)           | Returns the dimension of a vector                   |
| [`VEC_L2_NORM`](#vec_l2_norm)     | Calculates the L2 norm (Euclidean norm) of a vector |
| [`VEC_FROM_TEXT`](#vec_from_text) | Converts a string into a vector                     |
| [`VEC_AS_TEXT`](#vec_as_text)     | Converts a vector into a string                     |
## Extended built-in functions and operators

The following built-in functions and operators are extended to support operations on [Vector data types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types).

**Arithmetic operators:**

| Name                                                                                    | Description                              |
| :-------------------------------------------------------------------------------------- | :--------------------------------------- |
| [`+`](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_plus)  | Vector element-wise addition operator    |
| [`-`](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_minus) | Vector element-wise subtraction operator |

For more information about how vector arithmetic works, see [Vector Data Type | Arithmetic](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types#arithmetic).

**Aggregate (GROUP BY) functions:**

| Name                                                                                                          | Description                                      |
| :------------------------------------------------------------------------------------------------------------ | :----------------------------------------------- |
| [`COUNT()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_count)                  | Return a count of the number of rows returned    |
| [`COUNT(DISTINCT)`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_count-distinct) | Return the count of a number of different values |
| [`MAX()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_max)                      | Return the maximum value                         |
| [`MIN()`](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_min)                      | Return the minimum value                         |

**Comparison functions and operators:**

| Name                                                                                                                | Description                                           |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| [`BETWEEN ... AND ...`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_between)         | Check whether a value is within a range of values     |
| [`COALESCE()`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_coalesce)                 | Return the first non-NULL argument                    |
| [`=`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_equal)                             | Equal operator                                        |
| [`<=>`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_equal-to)                        | NULL-safe equal to operator                           |
| [`>`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_greater-than)                      | Greater than operator                                 |
| [`>=`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_greater-than-or-equal)            | Greater than or equal operator                        |
| [`GREATEST()`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_greatest)                 | Return the largest argument                           |
| [`IN()`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_in)                             | Check whether a value is within a set of values       |
| [`IS NULL`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is-null)                     | Test whether a value is `NULL`                        |
| [`ISNULL()`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_isnull)                     | Test whether the argument is `NULL`                   |
| [`LEAST()`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_least)                       | Return the smallest argument                          |
| [`<`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_less-than)                         | Less than operator                                    |
| [`<=`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_less-than-or-equal)               | Less than or equal operator                           |
| [`NOT BETWEEN ... AND ...`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-between) | Check whether a value is not within a range of values |
| [`!=`, `<>`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-equal)                  | Not equal operator                                    |
| [`NOT IN()`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-in)                     | Check whether a value is not within a set of values   |

For more information about how vectors are compared, see [Vector Data Type | Comparison](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types#comparison).

**Control flow functions:**

| Name                                                                                              | Description                    |
| :------------------------------------------------------------------------------------------------ | :----------------------------- |
| [`CASE`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#operator_case)       | Case operator                  |
| [`IF()`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#function_if)         | If/else construct              |
| [`IFNULL()`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#function_ifnull) | Null if/else construct         |
| [`NULLIF()`](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#function_nullif) | Return `NULL` if expr1 = expr2 |

**Cast functions:**

| Name                                                                                        | Description                        |
| :------------------------------------------------------------------------------------------ | :--------------------------------- |
| [`CAST()`](https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html#function_cast)       | Cast a value as a string or vector |
| [`CONVERT()`](https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html#function_convert) | Cast a value as a string           |

For more information about how to use `CAST()`, see [Vector Data Type | Cast](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types#cast).
